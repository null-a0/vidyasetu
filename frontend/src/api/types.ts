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
  enrollment_count?: number | null;
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
  educator_type?: string | null;
  phone?: string | null;
  institution_id?: string | null;
  profile_photo?: string | null;
  bio?: string | null;
  department?: string | null;
  parent_name?: string | null;
  parent_email?: string | null;
  institution_admin_name?: string | null;
  institution_admin_address?: string | null;
  institution_admin_code?: string | null;
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

export interface BackendQuestionOption {
  id: string;
  text: string;
  is_correct?: boolean;
}

export interface BackendQuestion {
  id: string;
  assessment_id?: string | null;
  text?: string | null;
  type?: string | null;
  marks?: number | null;
  options: BackendQuestionOption[];
}

export interface BackendLeaderboardEntry {
  rank: number;
  student_id: string;
  student_name: string;
  average_percentage: number;
  attempts: number;
  passed: number;
}

export interface BackendAssessmentLeaderboard {
  assessment_id: string;
  entries: BackendLeaderboardEntry[];
}

export interface BackendWorkshopLeaderboard {
  workshop_id: string;
  entries: BackendLeaderboardEntry[];
}

export interface BackendDashboardSeriesPoint {
  label: string;
  value: number;
}

export interface BackendDashboardAlertItem {
  id: string;
  text: string;
  level: string;
}

export interface BackendDashboardActivityItem {
  id: string;
  text: string;
  time: string;
  type: string;
}

export interface BackendInstitutionDashboardAggregate {
  kpis: Record<string, number | string>;
  alerts: BackendDashboardAlertItem[];
  activity_feed: BackendDashboardActivityItem[];
  attendance_trend: BackendDashboardSeriesPoint[];
  enrollment_trend: BackendDashboardSeriesPoint[];
  report_cards: Record<string, number | string>;
}

export interface BackendAdminDashboardInsights {
  weekly_activity: BackendDashboardSeriesPoint[];
  demographics: Array<{ range: string; male: number; female: number }>;
  activity_feed: BackendDashboardActivityItem[];
}

export interface BackendSubmissionReviewQuestion {
  question_id: string;
  question_text: string;
  selected_option_ids: string[];
  selected_option_texts: string[];
  correct_option_ids: string[];
  correct_option_texts: string[];
  earned_marks: number;
  max_marks: number;
  is_correct: boolean;
}

export interface BackendSubmissionReview {
  submission_id: string;
  assessment_id: string;
  student_id: string;
  score: number;
  total_marks: number;
  percentage: number;
  pass_fail: boolean;
  questions: BackendSubmissionReviewQuestion[];
}

export interface BackendParentMessageResponse {
  accepted: number;
  failed: number;
  message: string;
}
export interface BackendParentContactItem {
  student_id: string;
  parent_name?: string | null;
  parent_email?: string | null;
}

export interface BackendParentContactDirectory {
  items: BackendParentContactItem[];
  total: number;
}

export interface BackendWorkshopEducatorProfile {
  workshop_id: string;
  educator_id?: string | null;
  name: string;
  email: string;
  department: string;
  institution: string;
  bio: string;
}

export interface BackendInstitutionStudentRosterItem {
  id: string;
  name: string;
  email: string;
  workshop: string;
  status: string;
}

export interface BackendInstitutionStudentRoster {
  items: BackendInstitutionStudentRosterItem[];
  total: number;
}

export interface BackendInstitutionAttendanceRow {
  student: string;
  mon: boolean;
  tue: boolean;
  wed: boolean;
  thu: boolean;
  fri: boolean;
}

export interface BackendInstitutionAttendanceReport {
  rows: BackendInstitutionAttendanceRow[];
  total: number;
}

export interface BackendLeaderboardAttemptQuestion {
  question_id: string;
  question_text: string;
  selected_option_texts: string[];
  correct_option_texts: string[];
  earned_marks: number;
  max_marks: number;
  is_correct: boolean;
}

export interface BackendLeaderboardAttemptDetail {
  submission_id: string;
  submitted_at?: string | null;
  score: number;
  percentage: number;
  pass_fail: boolean;
  questions: BackendLeaderboardAttemptQuestion[];
}

export interface BackendLeaderboardStudentDrilldown {
  context_type: string;
  context_id: string;
  student_id: string;
  student_name: string;
  attempts: BackendLeaderboardAttemptDetail[];
  average_percentage: number;
  total_attempts: number;
}



export interface BackendCertificateRecommendationResponse {
  accepted: number;
  failed: number;
  message: string;
}

export interface BackendCertificateDownloadResponse {
  certificate_id: string;
  download_url: string;
}


export interface BackendMaterialDownloadResponse {
  module_id: string;
  material_id: string;
  download_url: string;
}


export interface BackendExportFileResponse {
  file_name: string;
  file_type: string;
  download_url: string;
}

export interface BackendInstitutionStudentBulkActionResponse {
  requested_students: number;
  affected_students: number;
  updated_enrollments: number;
  message: string;
}



export interface BackendAdminAIReportCreateRequest {
  institution_id?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  focus_areas?: string[];
  force_regenerate?: boolean;
}

export interface BackendAdminAIReportCreateResponse {
  report_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  from_cache: boolean;
  deduplicated: boolean;
}

export interface BackendAdminAIReportStatusResponse {
  report_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  error_details?: Record<string, unknown> | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BackendAdminAIReportRecommendation {
  title: string;
  action: string;
  rationale: string;
  priority: string;
}

export interface BackendAdminAIReportDataWindow {
  start_date?: string | null;
  end_date?: string | null;
  scope: string;
}

export interface BackendAdminAIReportResult {
  summary: string;
  key_insights: string[];
  risk_flags: string[];
  recommendations: BackendAdminAIReportRecommendation[];
  trend_highlights: string[];
  data_window: BackendAdminAIReportDataWindow;
  caveats: string[];
}

export interface BackendAdminAIReportResultResponse {
  report_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  result: BackendAdminAIReportResult;
  created_at?: string | null;
  updated_at?: string | null;
  prompt_version: string;
  model_name: string;
}

export interface BackendAdminAIReportHistoryItem {
  report_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  institution_id?: string | null;
  source_entity_type: string;
  source_entity_id: string;
  prompt_version: string;
  model_name: string;
  summary_preview?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BackendStudentExplanationRequest {
  submission_id: string;
  question_id: string;
  force_regenerate?: boolean;
}

export interface BackendStudentExplanationResult {
  why_it_was_wrong: string;
  correct_reasoning: string;
  common_mistake: string;
  hint_for_retry: string;
  confidence: number;
  follow_up_questions: string[];
}

export interface BackendStudentExplanationResponse {
  explanation_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  from_cache: boolean;
  explanation: BackendStudentExplanationResult;
}
