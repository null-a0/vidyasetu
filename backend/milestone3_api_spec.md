# VidyaSetu Complete API Specification (Milestone 3)

This document provides a comprehensive technical specification for the VidyaSetu backend API (v1).

---

## Global Standards

### Base URL
- Local: `http://localhost:8000/api/v1`

### Authentication
- **Mechanism**: OAuth2 Password Bearer with JWT Access/Refresh tokens.
- **Header**: `Authorization: Bearer <token>`
- **Tokens**:
    - `access_token`: Valid for 30 minutes (default).
    - `refresh_token`: Used to obtain new access tokens.

### Common Parameters
- **Pagination (`PaginationParams`)**:
    - `offset` (Query, int): Default `0`, min `0`. Number of records to skip.
    - `limit` (Query, int): Default `50`, min `1`, max `1000`. Max records to return.

### Standard Error Responses
- **401 Unauthorized**: Missing or invalid token.
- **403 Forbidden**: Insufficient role permissions or institution mismatch.
- **404 Not Found**: Resource does not exist.
- **409 Conflict**: State conflict (e.g., double submission, name conflict).
- **422 Unprocessable Entity**: Validation failure (Pydantic / type mismatch).

---

## 1. Authentication & Security (`/auth`)

### POST `/auth/register`
- **Purpose**: Create a new user account.
- **Request Body (`UserCreate`)**:
    - `name` (str): Required.
    - `email` (EmailStr): Required, unique.
    - `password` (str): Required.
    - `role` (UserRole): Optional. Enum: `admin`, `institution_admin`, `educator`, `student`. Default: `student`.
    - `institution_id` (str): Optional. Nullable.
    - `phone` (str): Optional. Nullable.
- **Response**: `UserResponse` (201 Created).

### POST `/auth/login`
- **Purpose**: Authenticate and receive JWT.
- **Request Body (`LoginRequest`)**: `email`, `password`.
- **Response** (`Token`): `access_token`, `refresh_token`, `token_type` ("bearer").

### POST `/auth/forgot-password`
- **Purpose**: Trigger reset flow. Returns 200 even if email not found (security best practice).
- **Request Body**: `email`.

### POST `/auth/reset-password`
- **Purpose**: Update password using verification (Note: Currently implemented via simple email/password check in `auth.py:125`).
- **Partial Implementation**: Currently lacks a secure one-time-token check; uses plaintext email/new_password.

---

## 2. User Profiles (`/users`)

### GET `/users/me`
- **Purpose**: Returns current authenticated user profile.
- **Response**: `UserResponse`.

### GET `/users/`
- **Purpose**: List users in current scope.
- **Role**: Admin (Global), Institution Admin (Scoped to institution).
- **Query Params**: Pagination.
- **Response**: `Page[UserResponse]`.

---

## 3. Workshops & Enrollment (`/workshops`, `/enrollments`)

### POST `/workshops/`
- **Purpose**: Create workshop.
- **Role**: Admin, Institution Admin, Educator.
- **Validation**: Non-Admins can only create for their own `institution_id`.
- **Request Body (`WorkshopCreate`)**:
    - `title` (str): Required.
    - `description` (str): Optional.
    - `start_date` (datetime): Optional. Nullable.
    - `end_date` (datetime): Optional. Nullable.
    - `institution_id` (str): Optional (Auto-assigned for InstAdmins).

### GET `/workshops/`
- **Scope**: Students see all. Staff see institution-internal only.

### POST `/enrollments/`
- **Purpose**: Enroll student in workshop.
- **Validation**: Students only enroll themselves. Staff can enroll anyone.
- **Request Body**: `student_id`, `workshop_id`.

---

## 4. Content Management (`/modules`, `/materials`)

### POST `/modules/`
- **Purpose**: Add module to workshop.
- **Request Body**: `workshop_id`, `title`, `order_index` (int, default 0).

### POST `/modules/{id}/materials/upload`
- **Purpose**: Multipart upload to module.
- **Logic**: Automatically assigns material type:
    - `"video"` for video content types.
    - `"text"` for `.md`, `.txt`, `.html`.
    - `"link"` for others.
- **Storage**: Saved to `media/modules/{module_id}/{filename}`.

---

## 5. Assessments & Grading (`/assessments`, `/tests`, `/submissions`)

### POST `/assessments/`
- **Purpose**: Create MCQ/MSQ assessment.
- **Request Body**: `workshop_id`, `module_id`, `title`, `total_marks`, `pass_mark`.

### POST `/tests/{assessment_id}/start`
- **Purpose**: Begin attempt.
- **Response**: `TestStartResponse`. Hides `is_correct` in `OptionItem`.
- **Logic**: Returns existing `PENDING` submission or creates new.

### POST `/tests/{assessment_id}/submit`
- **Purpose**: Grade the submission.
- **Logic**: Uses `grade_submission` service.
- **Response**: `GradeResult`. Status code 200. Persists `score`, `percentage`, `pass_fail`.

---

## 6. Certificates (`/certificates`)

### POST `/certificates/generate`
- **Purpose**: Issue certificate.
- **Background Task**: Triggers PDF generation via ReportLab/PIL.
- **Verification Code**: Derived/Unique.

### GET `/certificates/verify/{code}`
- **Purpose**: Public validation. No authentication required.

---

## 7. Analytics & Dashboards (`/analytics`, `/dashboard`)

### GET `/analytics/institution/dashboard`
- **Purpose**: High-level reporting (Enrollment trends, Pass rates).
- **Metrics**: `kpis`, `alerts`, `activity_feed`, `attendance_trend`, `enrollment_trend`.

### GET `/dashboard/student/{id}`
- **Purpose**: Summary stats (Workshops enrolled, Avg score, Certs earned).

---

## 8. Specialized Modules

### Bulk Operations (`/bulk`)
- **CSV Headers**: `name`, `email`, `password`, `phone`, `institution_id`.
- **Endpoints**: `/students/bulk-upload`, `/enrollments/bulk`, `/attendance/bulk`.

### Fees & Payments (`/fees`, `/payments`)
- **FeePlan**: `amount` (int), `billing_cycle` (str).
- **StudentFee**: Tracks `balance`.
- **Payment**: `method` ("upi", "card", "cash"), `reference` (Optional string).

### Approvals (`/approvals`)
- **Types**: `DELETE_WORKSHOP`, `DELETE_EDUCATOR`, `DELETE_STUDENT`.
- **Status**: `PENDING`, `APPROVED`, `REJECTED`.

---

## Implementation Gaps & Notes

1. **Monthly Reports**: No implementation found for periodic automated report generation (Story 14).
2. **Student Content Guard**: `GET /modules/{id}` currently lacks a check for active enrollment.
3. **Session Timing**: Attendance currently accepts any string for `status`; no hard enum restriction in code.
4. **Photo Storage**: Profile photos implemented as relative paths; frontend must prepend base URL.
