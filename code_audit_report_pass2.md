# VidyaSetu Code Audit Report — Pass 2

Date: 2026-04-10  
Scope: Full backend/frontend bug sweep with focus on critical auth/authorization and runtime/contract errors after Pass 1 fixes.

---

## Critical Bugs

### 1) Public self-registration allows privilege escalation to staff/admin roles
- **File paths:**
  - `backend/app/api/v1/auth.py:35-52`
  - `backend/app/schemas/user.py:30-41`
  - `frontend/src/pages/SignUp.tsx:12-16`
- **What is wrong:** `POST /auth/register` accepts `UserCreate` directly, including caller-provided `role` (and `institution_id`).
- **Why it is wrong:** Any unauthenticated user can create privileged accounts (`educator`, `institution_admin`, and API-level `admin` if crafted manually).
- **Severity:** **critical**
- **Runtime/user effect:** Full privilege escalation and tenant boundary bypass.
- **Certainty:** **definite**

### 2) Password reset endpoint enables account takeover without proof-of-ownership
- **File path:** `backend/app/api/v1/auth.py:125-144`
- **What is wrong:** `POST /auth/reset-password` requires only `email` and `new_password`; no reset token/OTP/challenge validation.
- **Why it is wrong:** Anyone knowing a valid email can reset that account password.
- **Severity:** **critical**
- **Runtime/user effect:** Account takeover.
- **Certainty:** **definite**

---

## High Severity Bugs

### 3) Enrollment endpoints still miss institution/workshop authorization boundaries
- **File path:** `backend/app/api/v1/enrollments.py`
- **Functions:** `enrol` (40-53), `list_by_student` (66-83), `list_by_workshop` (96-110), `update_one` (146-156), `delete_one` (169-179), `get_one` (123-133)
- **What is wrong:** Only student self-checks are present; staff paths are not institution-scoped.
- **Why it is wrong:** Staff can create/read/update/delete enrollments across other institutions.
- **Severity:** **high**
- **Runtime/user effect:** Cross-tenant data leakage and tampering.
- **Certainty:** **definite**

### 4) Modules API lacks scope checks for both reads and writes
- **File path:** `backend/app/api/v1/modules.py`
- **Functions:** `create` (42-48), `batch_reorder` (61-76), `get_one` (89-97), `update_one` (110-120), `delete_one` (133-141), `upload_material` (154-202)
- **What is wrong:** Routes rely on role checks but do not validate module/workshop institution ownership; `get_one` is open to any authenticated user.
- **Why it is wrong:** Students/staff can access or mutate modules outside allowed tenant/workshop scope if IDs are known.
- **Severity:** **high**
- **Runtime/user effect:** Unauthorized content access/edit.
- **Certainty:** **definite**

### 5) Sessions/attendance API is not institution-scoped and has over-broad read access
- **File path:** `backend/app/api/v1/sessions.py`
- **Functions:** `list_by_workshop` (68-82), `get_one` (95-103), plus staff write endpoints (`create`, `update_one`, `delete_one`, attendance endpoints)
- **What is wrong:** Read routes are available to any authenticated user; staff write routes do not verify workshop institution ownership.
- **Why it is wrong:** Cross-tenant session and attendance data can be read/modified.
- **Severity:** **high**
- **Runtime/user effect:** Unauthorized schedule/attendance exposure and tampering.
- **Certainty:** **definite**

### 6) Fees and payments student-record endpoints are not institution-scoped for staff
- **File paths:**
  - `backend/app/api/v1/fees.py:149-202`
  - `backend/app/api/v1/payments.py:33-49, 62-70, 83-101`
- **What is wrong:** Only student self-guards exist; staff can query and mutate arbitrary students' financial records.
- **Why it is wrong:** Missing tenant boundary checks for sensitive financial data.
- **Severity:** **high**
- **Runtime/user effect:** Cross-tenant fee/payment leakage and writes.
- **Certainty:** **definite**

### 7) Student dashboard stats endpoint is not institution-scoped for staff callers
- **File path:** `backend/app/api/v1/dashboard.py:78-113`
- **Function:** `student_stats`
- **What is wrong:** Endpoint blocks only student-to-other-student reads; staff can query any `student_id`.
- **Why it is wrong:** Institution staff should be limited to their institution.
- **Severity:** **high**
- **Runtime/user effect:** Cross-tenant student KPI leakage.
- **Certainty:** **definite**

### 8) Test-start endpoint lacks enrollment/tenant authorization
- **File path:** `backend/app/api/v1/tests.py:38-70`
- **Function:** `start_test`
- **What is wrong:** Student role is enforced, but there is no check that student can access the assessment workshop.
- **Why it is wrong:** Students can start attempts for assessments outside their enrolled institution/workshops if IDs are known.
- **Severity:** **high**
- **Runtime/user effect:** Unauthorized assessment participation.
- **Certainty:** **definite**

### 9) Submissions API still has unscoped endpoints and allows staff answer mutation
- **File path:** `backend/app/api/v1/submissions.py`
- **Functions:** `post_answers` (42-64), `get_result` (77-96), `list_by_student` (109-123)
- **What is wrong:** Only student self-check exists in these routes; staff are unrestricted by institution scope. `post_answers` permits non-student mutation of pending submissions.
- **Why it is wrong:** Cross-tenant access and potential grading integrity violations.
- **Severity:** **high**
- **Runtime/user effect:** Data leakage and unauthorized answer edits.
- **Certainty:** **definite**

### 10) Bulk enrollment/attendance endpoints have no tenant-boundary enforcement
- **File path:** `backend/app/api/v1/bulk.py`
- **Functions:** `bulk_enroll` (164-183), `bulk_attendance` (197-222)
- **What is wrong:** Staff role is required but no institution/workshop/session ownership checks are performed.
- **Why it is wrong:** Staff can bulk-write cross-tenant enrollment/attendance data.
- **Severity:** **high**
- **Runtime/user effect:** Large-scale unauthorized data corruption.
- **Certainty:** **definite**

---

## Medium Severity Bugs

### 11) Certificate list-by-student pagination is incorrect for institution-scoped staff
- **File path:** `backend/app/api/v1/certificates.py:173-198`
- **Function:** `list_by_student`
- **What is wrong:** Pagination is applied before institution filtering; returned `total` is `len(enriched)` for current page only.
- **Why it is wrong:** Results and counts become inconsistent/incomplete for staff scope.
- **Severity:** **medium**
- **Runtime/user effect:** Missing certificates and incorrect pagination UI behavior.
- **Certainty:** **definite**

---

## Still Fragile / Needs Policy Decision

### A) User self-profile update still allows `institution_id` mutation
- **File paths:**
  - `backend/app/api/v1/users.py:97-112`
  - `backend/app/schemas/user.py:55`
- **Concern:** Non-admin self updates can include `institution_id`.
- **Risk:** Tenant-link drift / integrity issues.
- **Severity:** **medium**
- **Certainty:** **suspicious** (depends on intended product policy)

### B) Duplicate enrollments are still possible
- **File paths:**
  - `backend/app/crud/crud_workshop.py:140-147`
  - `backend/app/models.py:176-187`
- **Concern:** No duplicate guard in CRUD and no `(student_id, workshop_id)` uniqueness constraint in model.
- **Risk:** Inflated counts, inconsistent enrollment state.
- **Severity:** **medium**
- **Certainty:** **suspicious** (confirm DB-level migration constraints)

---

## Validation Notes
- `frontend` tests: `npm run test -- --run` passed (4 files, 7 tests).
- `frontend` production build: passed in prior run.
- Backend syntax check: `python -m compileall backend/app` passed.
- Full backend functional tests were not runnable in this environment earlier without additional pytest setup in the backend runtime.
