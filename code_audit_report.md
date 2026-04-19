# VidyaSetu Code Audit Report

Date: 2026-04-03  
Scope: frontend pages/components, frontend API/client/adapters/hooks, backend routes/services/schemas/models, frontend?backend contract alignment.  
Out of scope in this pass: tests/test coverage review.

---

## Definite Bugs

### 1) Cross-tenant assessment read access is missing
- **File path:** `backend/app/api/v1/assessments.py`
- **Function:** `list_by_workshop`, `list_by_module`, `get_one`
- **What is wrong:** Any authenticated non-student can read assessments without institution/workshop access checks.
- **Why it is wrong:** Institution-admin/educator data should be institution-scoped.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Staff may see assessments from other institutions.
- **Certainty:** **definite**

### 2) Cross-tenant submission listing/review access is missing
- **File path:** `backend/app/api/v1/submissions.py`
- **Function:** `list_by_assessment`, `review_submission`
- **What is wrong:** Staff routes do not verify that the assessment/workshop belongs to caller’s institution.
- **Why it is wrong:** Missing authorization boundary for institution-scoped staff.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Staff can view other institutions’ submission data/question breakdown.
- **Certainty:** **definite**

### 3) Analytics endpoints are not institution-scoped for staff
- **File path:** `backend/app/api/v1/analytics.py`
- **Function:** `student_analytics`, `student_attendance`, `workshop_analytics`, leaderboard/drilldown endpoints
- **What is wrong:** Non-student callers are not restricted to institution scope.
- **Why it is wrong:** Staff can query analytics for unrelated institutions.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Potential cross-tenant analytics leakage.
- **Certainty:** **definite**

### 4) Materials download endpoint lacks enrollment/institution checks
- **File path:** `backend/app/api/v1/materials.py`
- **Function:** `download_material`
- **What is wrong:** Any authenticated user can request material download by module/material ID.
- **Why it is wrong:** No authorization check ties student to enrollment or staff to institution.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Unauthorized material access if IDs are known/guessable.
- **Certainty:** **definite**

### 5) Certificate list by student lacks staff scope validation
- **File path:** `backend/app/api/v1/certificates.py`
- **Function:** `list_by_student`
- **What is wrong:** Only student self-check exists; institution-admin/educator can request any student’s certificates.
- **Why it is wrong:** Missing institution boundary checks.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Cross-institution certificate visibility.
- **Certainty:** **definite**

### 6) Educator can fetch arbitrary user profiles
- **File path:** `backend/app/api/v1/users.py`
- **Function:** `get_user_by_id`
- **What is wrong:** Restriction exists for students and institution-admin, but not for educator scope.
- **Why it is wrong:** Educator can read users outside institution.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Privacy leak for user metadata.
- **Certainty:** **definite**

### 7) Institution-admin can update any institution record
- **File path:** `backend/app/api/v1/institutions.py`
- **Function:** `update_one`
- **What is wrong:** Route allows `INSTITUTION_ADMIN` but does not enforce same institution.
- **Why it is wrong:** Missing authorization guard.
- **Type:** Backend
- **Severity:** **high**
- **Runtime/user effect:** Unauthorized institution profile updates.
- **Certainty:** **definite**

### 8) Student attempts can include non-student identities
- **File path:** `backend/app/api/v1/tests.py`
- **Function:** `start_test`, `submit_test`
- **What is wrong:** Endpoints allow any authenticated role; only student-specific guard is conditional.
- **Why it is wrong:** Test submission should be student workflow (or explicitly role-scoped).
- **Type:** Backend
- **Severity:** **medium**
- **Runtime/user effect:** Staff accounts can create/submit assessment attempts as themselves or submit non-owned submissions.
- **Certainty:** **definite**

### 9) Workshop create from list view sends institution name as ID
- **File path:** `frontend/src/pages/workshops/WorkshopsList.tsx`
- **Function/component:** `WorkshopsList` (`createMutation` payload)
- **What is wrong:** `institution_id` is set from `formInst` free-text, not resolved ID.
- **Why it is wrong:** Backend expects institution UUID/string ID.
- **Type:** Contract mismatch
- **Severity:** **high**
- **Runtime/user effect:** Workshop create can fail or persist invalid institution references.
- **Certainty:** **definite**

### 10) Admin create workshop allows invalid institution mapping
- **File path:** `frontend/src/pages/dashboard/AdminDashboard.tsx`
- **Function/component:** `handleSaveCreate`
- **What is wrong:** Unmatched institution name produces `undefined` `institution_id` and still proceeds.
- **Why it is wrong:** UI requires institution text but does not guarantee backend-valid institution.
- **Type:** Contract mismatch
- **Severity:** **medium**
- **Runtime/user effect:** Workshop may be created without proper institution linkage.
- **Certainty:** **definite**

### 11) Assessment status/duration UI is not backed by backend contract
- **File path:** `frontend/src/pages/assessments/Assessments.tsx` and `frontend/src/api/adapters.ts`
- **Function/component:** `AssessmentsPage`, `adaptAssessments`
- **What is wrong:** Backend schema has no status/duration, but UI edits them; adapter hardcodes `status: "Published"`.
- **Why it is wrong:** UI implies persisted controls that are ignored.
- **Type:** Contract mismatch
- **Severity:** **high**
- **Runtime/user effect:** Students can see/take assessments that should be draft; admin edits appear saved but are not.
- **Certainty:** **definite**

### 12) MSQ workflow is broken end-to-end in frontend
- **File path:** `frontend/src/pages/assessments/Assessments.tsx`, `frontend/src/pages/assessments/AssessmentAttempt.tsx`
- **Function/component:** Question builder + attempt answer state
- **What is wrong:** Builder allows MSQ label but stores single correct index; attempt stores single selected option per question.
- **Why it is wrong:** Backend answer contract supports `selected_option_ids` array for MSQ.
- **Type:** Frontend/contract mismatch
- **Severity:** **high**
- **Runtime/user effect:** MSQ authoring/attempting is logically incorrect; grading outcomes are wrong.
- **Certainty:** **definite**

### 13) Student progress chart month bucketing is incorrect
- **File path:** `frontend/src/pages/reports/PerformanceReports.tsx`
- **Function/component:** `barData` computation
- **What is wrong:** Attempts parse human labels (e.g., `"Apr 3"`) as dates; parsing is unstable and often misses buckets.
- **Why it is wrong:** Source labels are display strings, not reliable timestamps.
- **Type:** Frontend
- **Severity:** **medium**
- **Runtime/user effect:** Monthly score trend can be wrong/empty/fallbacked despite available analytics.
- **Certainty:** **definite**

### 14) Parent-email modal in Notifications maps recipient emails to student emails, not parent directory
- **File path:** `frontend/src/pages/notifications/Notifications.tsx`
- **Function/component:** Email modal submit handler
- **What is wrong:** It resolves recipients by matching entered emails to `User.email` of students, then sends parent-email endpoint.
- **Why it is wrong:** UI says “Email Parents”; backend expects student IDs whose `parent_email` is used.
- **Type:** Contract mismatch
- **Severity:** **high**
- **Runtime/user effect:** Parent outreach can silently miss intended recipients or target wrong mapping assumptions.
- **Certainty:** **definite**

### 15) Workshop educator profile endpoint is not workshop-specific when multiple educators exist
- **File path:** `backend/app/api/v1/workshops.py`
- **Function:** `get_workshop_educator_profile`
- **What is wrong:** It uses institution educators, then returns `409` if more than one exists.
- **Why it is wrong:** Endpoint contract for workshop details is effectively unusable in common institutions.
- **Type:** Backend/contract
- **Severity:** **medium**
- **Runtime/user effect:** Educator tab shows “unable to load educator profile” for many workshops.
- **Certainty:** **definite**

### 16) Workshop student counts are not real in core workshop fetch path
- **File path:** `frontend/src/services/api.ts`
- **Function:** `fetchWorkshops` + `adaptWorkshopsPage`
- **What is wrong:** `studentsEnrolled` defaults to 0 because enrollment counts are never fetched/populated.
- **Why it is wrong:** Multiple dashboards/lists display this as live metric.
- **Type:** Frontend/contract mismatch
- **Severity:** **medium**
- **Runtime/user effect:** User-facing enrollment counts are incorrect across pages.
- **Certainty:** **definite**

### 17) Student dashboard still has non-backend learning actions
- **File path:** `frontend/src/pages/dashboard/StudentDashboard.tsx`
- **Function/component:** “Continue Learning” panel (`Read Material`, course progress synthesis)
- **What is wrong:** `Read Material` is toast-only; progress/completed modules are heuristic (date-based + defaults).
- **Why it is wrong:** Looks live but is not fully backend-driven truth.
- **Type:** Frontend
- **Severity:** **medium**
- **Runtime/user effect:** Inaccurate progress and non-functional material action.
- **Certainty:** **definite**

### 18) Enrollment query in StudentManagement truncates to first 50 students
- **File path:** `frontend/src/pages/manage/StudentManagement.tsx`
- **Function/component:** `enrollmentsQuery`
- **What is wrong:** Hard-coded `slice(0, 50)` before fetching enrollments.
- **Why it is wrong:** Large cohorts are partially represented with no warning.
- **Type:** Frontend
- **Severity:** **medium**
- **Runtime/user effect:** Incomplete workshop/status data for students beyond first 50.
- **Certainty:** **definite**

### 19) Salary management still uses hardcoded educator type and default salary fallback
- **File path:** `frontend/src/pages/manage/SalaryManagement.tsx`
- **Function/component:** records mapping (`type` fixed to `Internal`, `defaultSalary`)
- **What is wrong:** Type is not sourced from backend; salary defaults are synthetic.
- **Why it is wrong:** Live payroll UI should not fabricate compensation/type.
- **Type:** Frontend/contract mismatch
- **Severity:** **medium**
- **Runtime/user effect:** Wrong salary/type display and potentially incorrect bulk payment amounts.
- **Certainty:** **definite**

### 20) `useAuth.refreshUser` can force logout on transient `/users/me` errors
- **File path:** `frontend/src/hooks/useAuth.ts`
- **Function/component:** `refreshUser`
- **What is wrong:** Any fetch failure clears access+refresh tokens.
- **Why it is wrong:** Temporary server/network errors should not invalidate session state.
- **Type:** Frontend
- **Severity:** **medium**
- **Runtime/user effect:** Unexpected logout/session loss.
- **Certainty:** **definite**

---

## Suspicious / Fragile Areas (Manual Review Needed)

### A) Duplicate enrollments are not prevented in backend
- **File path:** `backend/app/crud/crud_workshop.py`
- **Function:** `create_enrollment`
- **Concern:** No unique check (`student_id`, `workshop_id`) before insert.
- **Type:** Backend
- **Severity:** **medium**
- **Likely effect:** Duplicate enrollments inflate counts and create inconsistent student state.
- **Certainty:** **suspicious** (depends on DB constraints/migration state)

### B) User self-profile update includes `institution_id`
- **File path:** `backend/app/api/v1/users.py`
- **Function:** `patch_user`
- **Concern:** Non-admin self-updates can carry `institution_id`.
- **Type:** Backend
- **Severity:** **medium**
- **Likely effect:** Tenant-link drift/data integrity issues.
- **Certainty:** **suspicious** (depends on intended policy)

### C) Materials upload modal captures title/type but upload API ignores both
- **File path:** `frontend/src/pages/materials/Materials.tsx`
- **Function/component:** upload modal + `uploadMutation`
- **Concern:** User-entered metadata is unused; backend derives title/type from file.
- **Type:** Contract mismatch
- **Severity:** **low**
- **Likely effect:** User confusion and mismatched expectations.
- **Certainty:** **definite**

### D) Profile update flow may over-post fields not editable in UI
- **File path:** `frontend/src/pages/profile/ProfilePage.tsx`
- **Function/component:** `handleSave`
- **Concern:** Sends `institution_id` even though user doesn’t explicitly edit institution on page.
- **Type:** Frontend/contract
- **Severity:** **low**
- **Likely effect:** Hard-to-track profile/institution side effects if state is stale.
- **Certainty:** **suspicious**

### E) Multiple UI strings show encoding corruption
- **File path:** multiple frontend/backend files (examples: `frontend/src/pages/...`, `backend/app/...` comments)
- **Function/component:** UI text constants/messages
- **Concern:** Mojibake text like `â€”`, `â€¢`, `Â©` appears in rendered strings.
- **Type:** Frontend
- **Severity:** **low**
- **Likely effect:** User-visible text quality issues.
- **Certainty:** **definite**

---

## Integration Mismatches (Frontend ? Backend Contract)

### I1) Assessment status/duration fields are UI-only
- **Frontend:** `frontend/src/pages/assessments/Assessments.tsx`
- **Backend contract:** `backend/app/schemas/assessment.py` (`AssessmentCreate/Update` has no status/duration)
- **Mismatch:** UI edits non-existent backend fields.
- **Severity:** **high**
- **Effect:** False sense of publish/draft control.
- **Certainty:** **definite**

### I2) Material type taxonomy mismatch
- **Frontend:** `frontend/src/api/adapters.ts`, `frontend/src/pages/materials/Materials.tsx`
- **Backend:** `backend/app/api/v1/modules.py`, `backend/app/schemas/workshop.py`
- **Mismatch:** Backend material types are `video|text|link`; UI expects file-like `PDF|PPTX|DOC|TXT` semantics.
- **Severity:** **medium**
- **Effect:** Incorrect badges/icons and ambiguous UX.
- **Certainty:** **definite**

### I3) Admin demographics payload semantics are misleading
- **Frontend:** `frontend/src/pages/dashboard/AdminDashboard.tsx` (male/female bars)
- **Backend:** `backend/app/api/v1/analytics.py::admin_insights`
- **Mismatch:** Backend populates `male` with institution student count and `female` as 0.
- **Severity:** **medium**
- **Effect:** Chart appears gender-based but is actually institution distribution.
- **Certainty:** **definite**

### I4) Workshop educator profile contract does not support common workshop cases
- **Frontend:** `frontend/src/pages/workshops/WorkshopDetails.tsx`
- **Backend:** `backend/app/api/v1/workshops.py::get_workshop_educator_profile`
- **Mismatch:** Endpoint returns conflict for multi-educator institutions instead of workshop-specific mapping.
- **Severity:** **medium**
- **Effect:** Educator block frequently fails to render real profile.
- **Certainty:** **definite**

### I5) Parent communication flow split-brain between pages
- **Frontend pages:** `StudentManagement.tsx` vs `Notifications.tsx`
- **Backend:** `backend/app/api/v1/communication.py`
- **Mismatch:** One page uses student IDs from directory (correct), another infers student IDs from typed emails (fragile/wrong for “parent email”).
- **Severity:** **high**
- **Effect:** Inconsistent dispatch behavior and failed parent outreach.
- **Certainty:** **definite**

---

## Dead / Stale Code Still Present

### D1) Mock domain model module still defines live-like sample arrays
- **File path:** `frontend/src/mock/mockData.ts`
- **What is stale:** Large mock datasets remain while live pages import only types.
- **Type:** Frontend dead/stale code
- **Severity:** **low**
- **Effect:** Confusing maintenance surface; risk of accidental reintroduction.
- **Certainty:** **definite**

### D2) Many live files still import types from mock module
- **File paths (examples):**
  - `frontend/src/pages/dashboard/AdminDashboard.tsx`
  - `frontend/src/pages/dashboard/StudentDashboard.tsx`
  - `frontend/src/pages/materials/Materials.tsx`
  - `frontend/src/pages/submissions/Submissions.tsx`
  - `frontend/src/routes/ProtectedRoute.tsx`
- **What is stale:** Runtime is API-driven, but type layer is coupled to mock module.
- **Type:** Frontend dead/stale coupling
- **Severity:** **low**
- **Effect:** Architectural drift and brittle typings.
- **Certainty:** **definite**

### D3) UI-only quick actions remain in live dashboards
- **File paths:**
  - `frontend/src/pages/dashboard/AdminDashboard.tsx`
  - `frontend/src/pages/dashboard/StudentDashboard.tsx`
  - `frontend/src/pages/dashboard/InstitutionDashboard.tsx` (selected row action toast)
- **What is stale:** Multiple buttons still perform toast/navigation placeholders without domain-side operation.
- **Type:** Frontend
- **Severity:** **low/medium**
- **Effect:** UI appears actionable but is partially disconnected.
- **Certainty:** **definite**

---

## Prioritized Top Issues to Fix First

1. **Enforce institution-level authorization on backend analytics/assessments/submissions/materials/certificates/users endpoints** (high-risk data leakage).  
2. **Fix assessment workflow contract mismatch**: remove fake status/duration assumptions, prevent draft-from-being-attemptable, and implement real MSQ UI model.  
3. **Correct workshop create payloads** in list/admin dashboards so `institution_id` is always valid backend ID.  
4. **Replace incorrect parent-email recipient resolution in Notifications** with parent directory-backed selection.  
5. **Make workshop educator profile workshop-specific** (or provide deterministic mapping) to stop frequent educator profile failures.  
6. **Remove synthetic enrollment/salary/progress placeholders in live views** (`studentsEnrolled`, salary defaults, heuristic progress).  
7. **Harden auth session resilience** in `useAuth.refreshUser` to avoid token purge on transient failures.  

---

## Notes
- This audit is code-evidence based and intentionally conservative.
- Findings marked **suspicious** need policy/intent confirmation before code changes.
