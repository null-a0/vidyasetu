# VidyaSetu API Inventory & User Story Mapping (Milestone 3)

This report provides a comprehensive mapping of the VidyaSetu backend API endpoints to the functional requirements defined in the User Stories (EPICs 1-6).

## 1. User Story Mapping

### EPIC 1: User Authentication and Role Management

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1.1 | Admin | Secure login & administrative access | `/api/v1/auth/login` | POST | Full | JWT, Role: admin | Sync |
| 5.1.2 | Educator | Secure login & workshop access | `/api/v1/auth/login` | POST | Full | JWT, Role: educator | Sync |

**Gaps/Missing Behavior**:
- None identified for login. Role-based access is strictly enforced via `require_role` dependency.

---

### EPIC 2: Content Management

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.2.1 | Educator | Upload study materials (notes, etc.) | `/api/v1/modules/`, `/api/v1/modules/{id}/materials/upload` | POST | Full | JWT, Staff roles | Multi-step (create module -> upload) |
| 5.2.2 | Student | Access study materials | `/api/v1/workshops/{id}/modules`, `/api/v1/modules/{id}` | GET | Partial | JWT, Any role | Sync |

**Gaps/Missing Behavior**:
- **Security Gap**: `GET /api/v1/modules/{module_id}` does not strictly verify if a `STUDENT` is enrolled in the parent workshop before serving content.

---

### EPIC 3: Assessment Management

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.3.1 | Educator | Create and manage assessments | `/api/v1/assessments/`, `/api/v1/assessments/{id}/questions` | POST | Full | JWT, Staff roles | Multi-step |
| 5.3.2 | Student | Attempt assessments digitally | `/api/v1/tests/{id}/start`, `/api/v1/submissions/{id}/answers` | POST | Partial | JWT, Role: student | Multi-step |
| 5.3.3 | Educator | Automatic evaluation of assessments | `/api/v1/tests/{id}/submit` | POST | Full | JWT, Owner only | Sync (Auto-grader) |

**Gaps/Missing Behavior**:
- **Security Gap**: `POST /api/v1/tests/{assessment_id}/start` missing enrollment check; any authenticated student can start a test if the ID is known.

---

### EPIC 4: Certificate Management

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.4.1 | Admin | Automatic certificate generation | `/api/v1/certificates/generate` | POST | Full | JWT, Staff roles | Async/Background |
| 5.4.2 | Verifier | Public certificate verification | `/api/v1/certificates/verify/{code}` | GET | Full | Public (No Auth) | Sync |

---

### EPIC 5: Performance Tracking and Reporting

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.5.1 | Admin | Track performance across workshops | `/api/v1/analytics/workshop/{id}`, `/api/v1/analytics/student/{id}` | GET | Full | JWT, Staff roles | Sync |
| 5.5.2 | Student | View own results and reports | `/api/v1/analytics/student/{id}`, `/api/v1/submissions/student/{id}` | GET | Full | JWT, Own data | Sync |
| 5.5.3 | Admin | View workshop statistics | `/api/v1/analytics/institution/dashboard`, `/api/v1/analytics/admin/insights` | GET | Full | JWT, Admin roles | Sync |

---

### EPIC 6: Notification and Communication

| Story ID | Role | Business Goal | Backend Endpoint(s) | Method(s) | Status | Validation / RBAC | Flow |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5.6.1 | Admin | Notify students/parents | `/api/v1/notifications/send`, `/api/v1/communication/parent-email` | POST | Full | JWT, Staff roles | Sync |
| 5.6.2 | Admin | Automatic monthly report generation | — | — | Missing | — | — |

**Gaps/Missing Behavior**:
- **Story 5.6.2 (Monthly Reports)**: No backend implementation or scheduler discovered for automatic monthly report generation.

---

## 2. Discovered Backend Endpoints (Inventory)

The following groups of endpoints were found in the `app/api/v1` routers:

### Authentication (`/auth`)
- `POST /register`: User self-registration.
- `POST /login`: JWT token issuance.
- `POST /refresh`: Token refresh.
- `POST /forgot-password`: Reset flow initiation.
- `POST /reset-password`: Finalize password change.

### Users (`/users`)
- `GET /`: List users (Admin/InstAdmin only).
- `GET /me`: Get self profile.
- `GET /{id}`: Get user by ID.
- `PATCH /{id}`: Update profile.

### Workshops (`/workshops`)
- `POST /`: Create workshop.
- `GET /`: List workshops (scoped).
- `GET /{id}`: Get workshop details.
- `PATCH /{id}`: Update workshop.
- `DELETE /{id}`: Delete workshop.

### Content & Modules (`/modules`, `/materials`)
- `POST /modules/`: Create module.
- `PATCH /modules/reorder`: Batch reorder.
- `POST /modules/{id}/materials/upload`: File upload.
- `PATCH /materials/{module_id}/{material_id}`: Update material metadata.

### Assessments & Submissions (`/assessments`, `/tests`, `/submissions`)
- `POST /assessments/`: Create assessment.
- `POST /assessments/{id}/questions`: Add questions.
- `POST /tests/{id}/start`: Initialize attempt.
- `POST /tests/{id}/submit`: Grade and finalize.
- `POST /submissions/{id}/answers`: Save progress.
- `GET /submissions/{id}/review`: Staff view of graded answers.

### Analytics (`/analytics`)
- `GET /student/{id}`: Student performance trends.
- `GET /attendance/{id}`: Student attendance history.
- `GET /workshop/{id}`: Workshop-level stats.
- `GET /institution/dashboard`: High-level aggregate data.

### Other Components
- **Institutions**: Full CRUD on `/institutions/` (Admin only).
- **Enrollments**: Manage student-workshop links on `/enrollments/`.
- **Sessions & Attendance**: Create sessions and mark attendance on `/sessions/`.
- **Certificates**: Generate and verify on `/certificates/`.
- **Notifications**: Send and read on `/notifications/`.

---

## 3. Implementation Gaps

### Unimplemented User Stories
- **5.6.2 Monthly report generation**: No automated logic or endpoint exists to compile and distribute monthly reports.

### Missing Validation/Logic in Backend
- **Enrollment Verification**: Several student-facing endpoints (modules, assessments, starting tests) lack a strict enrollment check. An authenticated student can currently access content for any workshop if they possess the resource ID.
- **Parent Notifications**: While `/communication/parent-email` exists, it currently logs a notification for the *student*. Real external email dispatch logic is not visible in the provided routers.

### Extra Backend Features (Not in Stories)
- **Fee Management**: Robust system for Fee Plans, Assignments, and Balances (`/api/v1/fees`).
- **Payment Processing**: Recording of payments and balance updates (`/api/v1/payments`).
- **Salary Management**: Endpoints for tracking staff salaries (`/api/v1/salaries`).
- **Bulk Operations**: High-performance CSV uploads for students, enrollments, and attendance (`/api/v1/bulk`).
- **Approval System**: Workflow for approving various entities (`/api/v1/approvals`).
