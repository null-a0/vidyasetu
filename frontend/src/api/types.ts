export interface ApiPage<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface BackendWorkshop {
  id: string;
  title?: string | null;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  institution_id?: string | null;
}

export interface BackendModule {
  id: string;
  workshop_id?: string | null;
  title?: string | null;
  order_index?: number | null;
  materials: BackendMaterialItem[];
}

export interface BackendMaterialItem {
  id: string;
  title: string;
  type: string;
  content: string;
  created_at?: string | null;
}

export interface BackendAssessment {
  id: string;
  workshop_id?: string | null;
  module_id?: string | null;
  title?: string | null;
  total_marks?: number | null;
  pass_mark?: number | null;
}

export interface BackendEnrollment {
  id: string;
  student_id?: string | null;
  workshop_id?: string | null;
  status?: string | null;
  enrolled_at?: string | null;
}

export interface BackendCertificate {
  id: string;
  student_id?: string | null;
  workshop_id?: string | null;
  issue_date?: string | null;
  verification_code?: string | null;
  qr_url?: string | null;
  pdf_path?: string | null;
  student_name?: string | null;
  workshop_title?: string | null;
}

export interface BackendNotification {
  id: string;
  user_id?: string | null;
  message?: string | null;
  status?: string | null;
  notification_type?: string | null;
  created_at?: string | null;
}

export interface BackendUser {
  id: string;
  name?: string | null;
  email: string;
  role: string;
  phone?: string | null;
  institution_id?: string | null;
  theme?: string | null;
}

export interface AdminStatsResponse {
  total_institutions: number;
  total_workshops: number;
  total_educators: number;
  total_students: number;
  certificates_issued: number;
  active_workshops: number;
}

export interface StudentStatsResponse {
  enrolled_workshops: number;
  completed_assessments: number;
  average_score: number;
  certificates_earned: number;
}

export interface DashboardStatsResponse {
  assigned_workshops: number;
  materials_uploaded: number;
  active_assessments: number;
  pending_submissions: number;
}

export interface BackendScoreTrendPoint {
  assessment_id?: string | null;
  score?: number | null;
  percentage?: number | null;
  pass_fail?: boolean | null;
  submitted_at?: string | null;
}

export interface BackendStudentAssessmentAnalytics {
  total_submissions: number;
  avg_score: number;
  avg_percentage: number;
  passed: number;
  failed: number;
  score_trend: BackendScoreTrendPoint[];
}

export interface BackendStudentAttendanceAnalytics {
  total_sessions: number;
  present: number;
  late: number;
  absent: number;
  attendance_percentage: number;
}

export interface BackendStudentAnalytics {
  student_id: string;
  enrolled_workshops: number;
  assessment: BackendStudentAssessmentAnalytics;
  attendance: BackendStudentAttendanceAnalytics;
}

export interface BackendWorkshopEnrollmentAnalytics {
  total_enrolled: number;
  completed: number;
  dropped: number;
  active: number;
}

export interface BackendWorkshopAssessmentAnalytics {
  total_submissions: number;
  avg_score: number;
  avg_percentage: number;
  pass_rate_percentage: number;
}

export interface BackendWorkshopAttendanceAnalytics {
  total_attendance_records: number;
  avg_attendance_percentage: number;
}

export interface BackendWorkshopAnalytics {
  workshop_id: string;
  enrollment: BackendWorkshopEnrollmentAnalytics;
  assessment: BackendWorkshopAssessmentAnalytics;
  attendance: BackendWorkshopAttendanceAnalytics;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface BackendSubmission {
  id: string;
  student_id?: string | null;
  assessment_id?: string | null;
  score?: number | null;
  percentage?: number | null;
  pass_fail?: boolean | null;
  submitted_at?: string | null;
}

export interface BackendInstitution {
  id: string;
  name: string;
  address?: string | null;
  admin_id?: string | null;
}

export interface BackendApprovalRequest {
  id: string;
  request_type: string;
  status: string;
  payload: Record<string, unknown>;
  requested_by?: string | null;
  created_at?: string | null;
  resolved_at?: string | null;
}

export interface BackendSalaryPayment {
  id: string;
  educator_id: string;
  month: string;
  amount: number;
  status: string;
  created_at?: string | null;
}
