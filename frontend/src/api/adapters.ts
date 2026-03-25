import type {
  BackendWorkshop,
  BackendModule,
  BackendAssessment,
  BackendCertificate,
  BackendNotification,
  ApiPage,
  AdminStatsResponse,
  StudentStatsResponse,
  DashboardStatsResponse,
} from './types';
import type {
  Workshop,
  Material,
  Assessment,
  Certificate,
  Notification,
  AdminStats,
  StudentStats,
  DashboardStats,
} from '@/mock/mockData';

const formatDate = (value?: string | null) => {
  if (!value) return '';
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Date(parsed).toISOString().split('T')[0];
};

const getWorkshopStatus = (start?: string | null, end?: string | null): Workshop['status'] => {
  const now = Date.now();
  const startMs = start ? Date.parse(start) : NaN;
  const endMs = end ? Date.parse(end) : NaN;
  if (!Number.isNaN(startMs) && !Number.isNaN(endMs)) {
    if (now >= startMs && now <= endMs) return 'Active';
    if (now < startMs) return 'Upcoming';
    return 'Completed';
  }
  if (!Number.isNaN(startMs)) {
    return now < startMs ? 'Upcoming' : 'Active';
  }
  return 'Upcoming';
};

export const adaptWorkshop = (
  workshop: BackendWorkshop,
  overrides?: {
    institutionName?: string;
    studentsEnrolled?: number;
    status?: Workshop['status'];
  }
): Workshop => ({
  id: workshop.id,
  name: workshop.title ?? 'Untitled Workshop',
  description: workshop.description ?? '',
  institution: overrides?.institutionName ?? workshop.institution_id ?? '',
  startDate: formatDate(workshop.start_date),
  endDate: formatDate(workshop.end_date),
  studentsEnrolled: overrides?.studentsEnrolled ?? 0,
  status: overrides?.status ?? getWorkshopStatus(workshop.start_date, workshop.end_date),
});

export const adaptWorkshopsPage = (
  page: ApiPage<BackendWorkshop>,
  options?: {
    institutionLookup?: Record<string, string>;
    enrollmentCounts?: Record<string, number>;
  }
): Workshop[] =>
  page.items.map((w) =>
    adaptWorkshop(w, {
      institutionName: options?.institutionLookup?.[w.institution_id ?? ''] ?? w.institution_id ?? '',
      studentsEnrolled: options?.enrollmentCounts?.[w.id] ?? 0,
    })
  );

export const adaptModulesToMaterials = (
  modules: BackendModule[],
  workshopLookup: Record<string, string>
): Material[] =>
  modules.flatMap((module) =>
    module.materials.map((material) => ({
      id: material.id,
      title: material.title,
      workshop: workshopLookup[module.workshop_id ?? ''] ?? '',
      fileType: material.type.toUpperCase(),
      uploadDate: formatDate(material.created_at),
    }))
  );

export const adaptAssessments = (
  assessments: BackendAssessment[],
  workshopLookup: Record<string, string>
): Assessment[] =>
  assessments.map((assessment) => ({
    id: assessment.id,
    title: assessment.title ?? 'Untitled Assessment',
    workshop: workshopLookup[assessment.workshop_id ?? ''] ?? '',
    totalMarks: assessment.total_marks ?? 0,
    passingMarks: assessment.pass_mark ?? 0,
    status: 'Published',
  }));

export const adaptCertificates = (
  certificates: BackendCertificate[],
  workshopLookup: Record<string, string>,
  studentLookup: Record<string, string> = {}
): Certificate[] =>
  certificates.map((cert) => ({
    id: cert.id,
    certificateId: cert.verification_code ?? cert.id,
    studentName: cert.student_name ?? studentLookup[cert.student_id ?? ''] ?? '',
    workshop: cert.workshop_title ?? workshopLookup[cert.workshop_id ?? ''] ?? '',
    completionDate: formatDate(cert.issue_date),
    status: cert.qr_url ? 'Issued' : 'Pending',
  }));

const notificationVisualType: Record<string, Notification['type']> = {
  general: 'info',
  test: 'info',
  fees: 'warning',
  attendance: 'info',
  certificate: 'success',
  unread: 'info',
  read: 'info',
};

export const adaptNotifications = (notifications: BackendNotification[]): Notification[] =>
  notifications.map((notif) => ({
    id: notif.id,
    title: notif.notification_type ? notif.notification_type.replace(/_/g, ' ') : 'Notification',
    message: notif.message ?? '',
    type: notificationVisualType[notif.notification_type ?? ''] ?? 'info',
    date: formatDate(notif.created_at),
    read: notif.status === 'read',
  }));

export const adaptAdminStats = (stats: AdminStatsResponse): AdminStats => ({
  totalInstitutions: stats.total_institutions,
  totalWorkshops: stats.total_workshops,
  totalEducators: stats.total_educators,
  totalStudents: stats.total_students,
  certificatesIssued: stats.certificates_issued,
  activeWorkshops: stats.active_workshops,
});

export const adaptStudentStats = (stats: StudentStatsResponse): StudentStats => ({
  enrolledWorkshops: stats.enrolled_workshops,
  completedAssessments: stats.completed_assessments,
  averageScore: stats.average_score,
  certificatesEarned: stats.certificates_earned,
});

export const adaptDashboardStats = (stats: DashboardStatsResponse): DashboardStats => ({
  assignedWorkshops: stats.assigned_workshops,
  materialsUploaded: stats.materials_uploaded,
  activeAssessments: stats.active_assessments,
  pendingSubmissions: stats.pending_submissions,
});
