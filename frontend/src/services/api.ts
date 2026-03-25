import { apiGet, apiPost, apiPatch, apiDelete } from '@/api/client';
import {
  adaptWorkshopsPage,
  adaptModulesToMaterials,
  adaptAssessments,
  adaptCertificates,
  adaptNotifications,
  adaptAdminStats,
  adaptStudentStats,
  adaptDashboardStats,
} from '@/api/adapters';
import type {
  ApiPage,
  BackendWorkshop,
  BackendModule,
  BackendAssessment,
  BackendEnrollment,
  BackendCertificate,
  BackendNotification,
  BackendUser,
  BackendInstitution,
  BackendApprovalRequest,
  BackendSalaryPayment,
  BackendSubmission,
  TokenResponse,
  AdminStatsResponse,
  StudentStatsResponse,
  DashboardStatsResponse,
} from '@/api/types';
import type {
  Workshop,
  Material,
  Assessment,
  Certificate,
  Notification,
  DashboardStats,
  Submission,
  Question,
} from '@/mock/mockData';
import { sampleQuestions } from '@/mock/mockData';

const WORKSHOP_LIMIT = 25;

const buildWorkshopLookup = (workshops: Workshop[]) => Object.fromEntries(workshops.map((w) => [w.id, w.name]));

const formatDateTime = (value?: string | null) => {
  if (!value) return '';
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Date(parsed).toISOString().slice(0, 16).replace('T', ' ');
};

export const fetchWorkshops = async (): Promise<Workshop[]> => {
  const data = await apiGet<ApiPage<BackendWorkshop>>('/workshops/', { params: { limit: WORKSHOP_LIMIT } });

  // Map institution_id -> name when possible (avoids showing raw UUIDs in the UI).
  let institutionLookup: Record<string, string> = {};
  try {
    const institutions = await apiGet<BackendInstitution[]>('/institutions/', { params: { limit: 200 } });
    institutionLookup = Object.fromEntries(institutions.map((i) => [i.id, i.name]));
  } catch {
    institutionLookup = {};
  }

  return adaptWorkshopsPage(data, { institutionLookup });
};

export const fetchWorkshop = async (workshopId: string): Promise<Workshop> => {
  const data = await apiGet<BackendWorkshop>('/workshops/' + workshopId);
  return adaptWorkshopsPage({ items: [data], total: 1, offset: 0, limit: 1 })[0];
};
export const createWorkshop = async (payload: {
  title: string;
  description?: string | null;
  institution_id?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}): Promise<Workshop> => {
  const data = await apiPost<BackendWorkshop>('/workshops/', payload);
  return adaptWorkshopsPage({ items: [data], total: 1, offset: 0, limit: 1 })[0];
};

export const updateWorkshop = async (
  workshopId: string,
  payload: { title?: string | null; description?: string | null; start_date?: string | null; end_date?: string | null }
): Promise<Workshop> => {
  const data = await apiPatch<BackendWorkshop>('/workshops/' + workshopId, payload);
  return adaptWorkshopsPage({ items: [data], total: 1, offset: 0, limit: 1 })[0];
};

export const deleteWorkshop = async (workshopId: string): Promise<void> => {
  await apiDelete<void>('/workshops/' + workshopId);
};

export const fetchMaterials = async (): Promise<Material[]> => {
  const data = await apiGet<ApiPage<BackendWorkshop>>('/workshops/', { params: { limit: 6 } });
  const workshopLookup = Object.fromEntries(data.items.map((item) => [item.id, item.title ?? '']));
  const modulePages = await Promise.all(
    data.items.map((workshop) =>
      apiGet<ApiPage<BackendModule>>('/workshops/' + workshop.id + '/modules', { params: { limit: 20 } })
    )
  );
  const modules = modulePages.flatMap((page) => page.items);
  return adaptModulesToMaterials(modules, workshopLookup);
};

export const fetchAssessments = async (): Promise<Assessment[]> => {
  const data = await apiGet<ApiPage<BackendWorkshop>>('/workshops/', { params: { limit: 6 } });
  const workshopLookup = Object.fromEntries(data.items.map((item) => [item.id, item.title ?? '']));
  const assessmentPages = await Promise.all(
    data.items.map((workshop) =>
      apiGet<ApiPage<BackendAssessment>>('/assessments/workshop/' + workshop.id, { params: { limit: 20 } })
    )
  );
  const assessments = assessmentPages.flatMap((page) => page.items);
  return adaptAssessments(assessments, workshopLookup);
};

export const fetchQuestions = async (): Promise<Question[]> => {
  // The app does not yet select an assessment id; keep the current UI working.
  return sampleQuestions;
};

export const fetchWorkshopModules = async (workshopId: string): Promise<BackendModule[]> => {
  const page = await apiGet<ApiPage<BackendModule>>('/workshops/' + workshopId + '/modules', { params: { limit: 200 } });
  return page.items;
};

export const fetchWorkshopAssessments = async (workshopId: string): Promise<BackendAssessment[]> => {
  const page = await apiGet<ApiPage<BackendAssessment>>('/assessments/workshop/' + workshopId, { params: { limit: 200 } });
  return page.items;
};

export const fetchEnrollments = async (studentId: string): Promise<ApiPage<BackendEnrollment>> => {
  return apiGet<ApiPage<BackendEnrollment>>('/enrollments/student/' + studentId, { params: { limit: 200 } });
};

export const enrollInWorkshop = async (studentId: string, workshopId: string): Promise<BackendEnrollment> => {
  return apiPost<BackendEnrollment>('/enrollments/', { student_id: studentId, workshop_id: workshopId });
};

const fetchUserLookup = async (ids: string[]) => {
  const map: Record<string, string> = {};
  await Promise.all(
    ids.map(async (id) => {
      try {
        const result = await apiGet<BackendUser>('/users/' + id);
        map[id] = result.name ?? '';
      } catch {
        map[id] = '';
      }
    })
  );
  return map;
};

export const fetchCertificates = async (options: { studentId?: string; asStaff?: boolean } = {}): Promise<Certificate[]> => {
  const { studentId, asStaff } = options;
  const workshops = await fetchWorkshops();
  const workshopLookup = buildWorkshopLookup(workshops);

  let page: ApiPage<BackendCertificate> = { items: [], total: 0, offset: 0, limit: 0 };
  if (asStaff) {
    page = await apiGet<ApiPage<BackendCertificate>>('/certificates/', { params: { limit: 100 } });
  } else if (studentId) {
    page = await apiGet<ApiPage<BackendCertificate>>('/certificates/student/' + studentId, { params: { limit: 100 } });
  }

  const missingStudentIds = Array.from(
    new Set(page.items.filter((c) => !c.student_name).map((item) => item.student_id).filter(Boolean))
  ) as string[];
  const studentLookup = missingStudentIds.length > 0 ? await fetchUserLookup(missingStudentIds) : {};
  return adaptCertificates(page.items, workshopLookup, studentLookup);
};

export const verifyCertificate = async (verificationCode: string): Promise<BackendCertificate> => {
  return apiGet<BackendCertificate>('/certificates/verify/' + encodeURIComponent(verificationCode));
};

export const fetchNotifications = async (userId: string): Promise<Notification[]> => {
  const data = await apiGet<ApiPage<BackendNotification>>('/notifications/' + userId, { params: { limit: 50 } });
  return adaptNotifications(data.items);
};

export const fetchSubmissions = async (): Promise<Submission[]> => {
  const workshopPage = await apiGet<ApiPage<BackendWorkshop>>('/workshops/', { params: { limit: 6 } });
  const assessmentPages = await Promise.all(
    workshopPage.items.map((workshop) =>
      apiGet<ApiPage<BackendAssessment>>('/assessments/workshop/' + workshop.id, { params: { limit: 50 } })
    )
  );
  const assessments = assessmentPages.flatMap((page) => page.items);
  const assessmentLookup = Object.fromEntries(assessments.map((a) => [a.id, a.title ?? 'Assessment']));

  const submissionPages = await Promise.all(
    assessments.map(async (assessment) => {
      try {
        return await apiGet<ApiPage<BackendSubmission>>('/submissions/assessment/' + assessment.id, { params: { limit: 200 } });
      } catch {
        return { items: [], total: 0, offset: 0, limit: 0 } as ApiPage<BackendSubmission>;
      }
    })
  );

  const submissions = submissionPages.flatMap((page) => page.items);
  const studentIds = Array.from(new Set(submissions.map((s) => s.student_id).filter(Boolean))) as string[];
  const studentLookup = await fetchUserLookup(studentIds);

  return submissions.map((s) => ({
    id: s.id,
    studentName: studentLookup[s.student_id ?? ''] ?? '',
    assessment: assessmentLookup[s.assessment_id ?? ''] ?? 'Assessment',
    score: s.score ?? 0,
    status: s.pass_fail === null || s.pass_fail === undefined ? 'Pending' : 'Graded',
    submittedAt: formatDateTime(s.submitted_at),
  }));
};

export const fetchAdminStats = async () => {
  const data = await apiGet<AdminStatsResponse>('/dashboard/admin');
  return adaptAdminStats(data);
};

export const fetchStudentStats = async (studentId: string) => {
  const data = await apiGet<StudentStatsResponse>('/dashboard/student/' + studentId);
  return adaptStudentStats(data);
};

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const data = await apiGet<DashboardStatsResponse>('/dashboard/educator');
  return adaptDashboardStats(data);
};

export const fetchCurrentUser = async () => {
  return apiGet<BackendUser>('/users/me');
};

export const registerUser = async (payload: { name: string; email: string; password: string; role: string }) => {
  return apiPost<BackendUser>('/auth/register', payload);
};

export const updateUser = async (
  userId: string,
  payload: { name?: string; phone?: string; profile_photo?: string; theme?: string; institution_id?: string }
) => {
  return apiPatch<BackendUser>('/users/' + userId, payload);
};

export const loginUser = async (payload: { email: string; password: string }) => {
  return apiPost<TokenResponse>('/auth/login', payload);
};

export const fetchStudents = async (): Promise<{ id: string; name: string }[]> => {
  const page = await apiGet<ApiPage<BackendUser>>('/users/', { params: { limit: 200 } });
  return page.items
    .filter((u) => u.role === 'student')
    .map((u) => ({ id: u.id, name: u.name ?? u.email }));
};

export const generateCertificate = async (payload: {
  studentId: string;
  workshopId: string;
}): Promise<BackendCertificate> => {
  return apiPost<BackendCertificate>('/certificates/generate', {
    student_id: payload.studentId,
    workshop_id: payload.workshopId,
  });
};

export const fetchInstitutions = async (): Promise<BackendInstitution[]> => {
  return apiGet<BackendInstitution[]>('/institutions/', { params: { limit: 200 } });
};

export const fetchUsers = async (options: { limit?: number; offset?: number } = {}): Promise<ApiPage<BackendUser>> => {
  const { limit = 200, offset = 0 } = options;
  const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
  return apiGet<ApiPage<BackendUser>>('/users/', { params: { limit: safeLimit, offset } });
};

export const fetchAllUsers = async (options: { max?: number } = {}): Promise<BackendUser[]> => {
  const max = options.max ?? 500;
  const limit = 200;
  let offset = 0;
  let items: BackendUser[] = [];

  while (items.length < max) {
    const page = await fetchUsers({ limit, offset });
    items = items.concat(page.items);
    if (page.items.length === 0) break;
    if (items.length >= page.total) break;
    offset += limit;
  }

  return items.slice(0, max);
};

export const fetchApprovalRequests = async (options: { status?: string; limit?: number; offset?: number } = {}) => {
  const { status, limit = 200, offset = 0 } = options;
  const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
  return apiGet<ApiPage<BackendApprovalRequest>>('/approvals/requests', {
    params: { limit: safeLimit, offset, ...(status ? { status } : {}) },
  });
};

export const createApprovalRequest = async (payload: { request_type: string; payload: Record<string, any> }) => {
  return apiPost<BackendApprovalRequest>('/approvals/requests', {
    request_type: payload.request_type,
    payload: payload.payload,
  });
};

export const approveApprovalRequest = async (requestId: string) => {
  return apiPost<BackendApprovalRequest>(`/approvals/requests/${requestId}/approve`);
};

export const rejectApprovalRequest = async (requestId: string) => {
  return apiPost<BackendApprovalRequest>(`/approvals/requests/${requestId}/reject`);
};

export const fetchSalaryPayments = async (options: { month?: string; limit?: number; offset?: number } = {}) => {
  const { month, limit = 200, offset = 0 } = options;
  const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
  return apiGet<ApiPage<BackendSalaryPayment>>('/salaries/', { params: { limit: safeLimit, offset, ...(month ? { month } : {}) } });
};

export const paySalary = async (payload: { educatorId: string; month: string; amount: number }) => {
  return apiPost<BackendSalaryPayment>('/salaries/pay', {
    educator_id: payload.educatorId,
    month: payload.month,
    amount: payload.amount,
  });
};

export const fetchWorkshopAnalytics = async (workshopId: string) => {
  return apiGet<Record<string, any>>('/analytics/workshop/' + workshopId);
};

export const fetchStudentAnalytics = async (studentId: string) => {
  return apiGet<Record<string, any>>('/analytics/student/' + studentId);
};
