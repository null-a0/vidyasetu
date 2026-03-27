# VidyaSetu API Documentation

## POST /api/v1/auth/register
**Summary**: Register a new user

### Request Body

- **name***: string
- **email***: string
- **password***: string
- **role**: string
- **institution_id**: string | null
- **phone**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **email***: string
- **role***: string
- **institution_id***: string | null
- **phone***: string | null
- **profile_photo***: string | null
- **theme***: string | null
- **created_at***: string | null

---

## POST /api/v1/auth/login
**Summary**: Obtain a JWT access token

### Request Body

- **email***: string
- **password***: string

### Response: 200/201 (JSON)

- **access_token***: string
- **token_type**: string

---

## POST /api/v1/auth/refresh
**Summary**: Refresh an access token

### Response: 200/201 (JSON)

- **access_token***: string
- **token_type**: string

---

## GET /api/v1/users/
**Summary**: List all users (admin only; institution_admin sees their institution only)

### Parameters
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **name***: string | null
  - **email***: string
  - **role***: string
  - **institution_id***: string | null
  - **phone***: string | null
  - **profile_photo***: string | null
  - **theme***: string | null
  - **created_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/users/me
**Summary**: Current authenticated user

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **email***: string
- **role***: string
- **institution_id***: string | null
- **phone***: string | null
- **profile_photo***: string | null
- **theme***: string | null
- **created_at***: string | null

---

## GET /api/v1/users/{user_id}
**Summary**: Fetch user by ID

### Parameters
- **user_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **email***: string
- **role***: string
- **institution_id***: string | null
- **phone***: string | null
- **profile_photo***: string | null
- **theme***: string | null
- **created_at***: string | null

---

## PATCH /api/v1/users/{user_id}
**Summary**: Update user profile

### Parameters
- **user_id*** (path): string

### Request Body

- **name**: string | null
- **phone**: string | null
- **profile_photo**: string | null
- **theme**: string | null
- **institution_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **email***: string
- **role***: string
- **institution_id***: string | null
- **phone***: string | null
- **profile_photo***: string | null
- **theme***: string | null
- **created_at***: string | null

---

## POST /api/v1/institutions/
**Summary**: Create institution (admin only)

### Request Body

- **name***: string
- **address**: string | null
- **admin_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **name***: string
- **address***: string | null
- **admin_id***: string | null

---

## GET /api/v1/institutions/
**Summary**: List institutions

### Parameters
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)
Array of [- **id***: string
- **name***: string
- **address***: string | null
- **admin_id***: string | null]

---

## GET /api/v1/institutions/{institution_id}
**Summary**: Get institution by ID

### Parameters
- **institution_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **name***: string
- **address***: string | null
- **admin_id***: string | null

---

## PATCH /api/v1/institutions/{institution_id}
**Summary**: Update institution (admin only)

### Parameters
- **institution_id*** (path): string

### Request Body

- **name**: string | null
- **address**: string | null
- **admin_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **name***: string
- **address***: string | null
- **admin_id***: string | null

---

## DELETE /api/v1/institutions/{institution_id}
**Summary**: Delete institution (admin only)

### Parameters
- **institution_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/workshops/
**Summary**: Create a workshop (admin / institution_admin / educator)

### Request Body

- **title***: string
- **description**: string | null
- **start_date**: string | null
- **end_date**: string | null
- **institution_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **title***: string | null
- **description***: string | null
- **start_date***: string | null
- **end_date***: string | null
- **institution_id***: string | null

---

## GET /api/v1/workshops/
**Summary**: List workshops (scoped by institution for non-admins)

### Parameters
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **title***: string | null
  - **description***: string | null
  - **start_date***: string | null
  - **end_date***: string | null
  - **institution_id***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/workshops/{workshop_id}
**Summary**: Get a workshop by ID

### Parameters
- **workshop_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **title***: string | null
- **description***: string | null
- **start_date***: string | null
- **end_date***: string | null
- **institution_id***: string | null

---

## PATCH /api/v1/workshops/{workshop_id}
**Summary**: Update a workshop

### Parameters
- **workshop_id*** (path): string

### Request Body

- **title**: string | null
- **description**: string | null
- **start_date**: string | null
- **end_date**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **title***: string | null
- **description***: string | null
- **start_date***: string | null
- **end_date***: string | null
- **institution_id***: string | null

---

## DELETE /api/v1/workshops/{workshop_id}
**Summary**: Delete a workshop (admin / institution_admin only)

### Parameters
- **workshop_id*** (path): string

### Response: No Content or File

---

## GET /api/v1/workshops/{workshop_id}/modules
**Summary**: List modules for a workshop

### Parameters
- **workshop_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **workshop_id***: string | null
  - **title***: string | null
  - **order_index***: integer | null
  - **materials**: Array of [- **id***: string
    - **title***: string
    - **type***: string
    - **content***: string
    - **created_at**: string | null]]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## POST /api/v1/modules/
**Summary**: Create a module

### Request Body

- **workshop_id***: string
- **title***: string
- **order_index**: integer
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## PATCH /api/v1/modules/reorder
**Summary**: Batch-reorder modules by setting their order_index values

### Request Body

- **items***: Array of [- **module_id***: string
  - **order_index***: integer]

### Response: 200/201 (JSON)
Array of [- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]]

---

## GET /api/v1/modules/{module_id}
**Summary**: Get a module by ID

### Parameters
- **module_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## PATCH /api/v1/modules/{module_id}
**Summary**: Update a module

### Parameters
- **module_id*** (path): string

### Request Body

- **title**: string | null
- **order_index**: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null] | null

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## DELETE /api/v1/modules/{module_id}
**Summary**: Delete a module

### Parameters
- **module_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/modules/{module_id}/materials/upload
**Summary**: Upload a material file and append it to the module's materials list

### Parameters
- **module_id*** (path): string

### Request Body

- **file***: string

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## PATCH /api/v1/materials/{module_id}/{material_id}
**Summary**: Update a single material item inside a module (staff only)

### Parameters
- **module_id*** (path): string
- **material_id*** (path): string

### Request Body

- **title**: string | null
- **type**: string | null
- **content**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## DELETE /api/v1/materials/{module_id}/{material_id}
**Summary**: Remove a single material item from a module (staff only)

### Parameters
- **module_id*** (path): string
- **material_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **order_index***: integer | null
- **materials**: Array of [- **id***: string
  - **title***: string
  - **type***: string
  - **content***: string
  - **created_at**: string | null]

---

## POST /api/v1/enrollments/
**Summary**: Enrol a student in a workshop

### Request Body

- **student_id***: string
- **workshop_id***: string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **status***: string | null
- **enrolled_at***: string | null

---

## GET /api/v1/enrollments/student/{student_id}
**Summary**: Get enrollments for a student

### Parameters
- **student_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **workshop_id***: string | null
  - **status***: string | null
  - **enrolled_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/enrollments/workshop/{workshop_id}
**Summary**: Get all enrollments for a workshop (staff only)

### Parameters
- **workshop_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **workshop_id***: string | null
  - **status***: string | null
  - **enrolled_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/enrollments/{enrollment_id}
**Summary**: Get a single enrollment

### Parameters
- **enrollment_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **status***: string | null
- **enrolled_at***: string | null

---

## PATCH /api/v1/enrollments/{enrollment_id}
**Summary**: Update enrollment status (staff only)

### Parameters
- **enrollment_id*** (path): string

### Request Body

- **status**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **status***: string | null
- **enrolled_at***: string | null

---

## DELETE /api/v1/enrollments/{enrollment_id}
**Summary**: Drop / delete an enrollment

### Parameters
- **enrollment_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/sessions/
**Summary**: Create a session (staff only)

### Request Body

- **workshop_id***: string
- **title***: string
- **start_time**: string | null
- **end_time**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **start_time***: string | null
- **end_time***: string | null

---

## GET /api/v1/sessions/workshop/{workshop_id}
**Summary**: List sessions for a workshop

### Parameters
- **workshop_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **workshop_id***: string | null
  - **title***: string | null
  - **start_time***: string | null
  - **end_time***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/sessions/{session_id}
**Summary**: Get a session by ID

### Parameters
- **session_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **start_time***: string | null
- **end_time***: string | null

---

## PATCH /api/v1/sessions/{session_id}
**Summary**: Update a session (staff only)

### Parameters
- **session_id*** (path): string

### Request Body

- **title**: string | null
- **start_time**: string | null
- **end_time**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **title***: string | null
- **start_time***: string | null
- **end_time***: string | null

---

## DELETE /api/v1/sessions/{session_id}
**Summary**: Delete a session (staff only)

### Parameters
- **session_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/sessions/{session_id}/attendance
**Summary**: Mark attendance for a session (staff only)

### Parameters
- **session_id*** (path): string

### Request Body

- **session_id***: string
- **student_id***: string
- **status***: string

### Response: 200/201 (JSON)

- **id***: string
- **session_id***: string | null
- **student_id***: string | null
- **status***: string | null

---

## GET /api/v1/sessions/{session_id}/attendance
**Summary**: Get attendance records for a session (staff only)

### Parameters
- **session_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **session_id***: string | null
  - **student_id***: string | null
  - **status***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## PATCH /api/v1/sessions/{session_id}/attendance/{attendance_id}
**Summary**: Update an attendance record (staff only)

### Parameters
- **session_id*** (path): string
- **attendance_id*** (path): string

### Request Body

- **status**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **session_id***: string | null
- **student_id***: string | null
- **status***: string | null

---

## POST /api/v1/assessments/
**Summary**: Create an assessment (staff only)

### Request Body

- **workshop_id***: string
- **module_id**: string | null
- **title***: string
- **total_marks**: integer
- **pass_mark**: integer

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **module_id***: string | null
- **title***: string | null
- **total_marks***: integer | null
- **pass_mark**: integer | null

---

## GET /api/v1/assessments/workshop/{workshop_id}
**Summary**: List assessments for a workshop

### Parameters
- **workshop_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **workshop_id***: string | null
  - **module_id***: string | null
  - **title***: string | null
  - **total_marks***: integer | null
  - **pass_mark**: integer | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/assessments/module/{module_id}
**Summary**: List assessments for a module

### Parameters
- **module_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **workshop_id***: string | null
  - **module_id***: string | null
  - **title***: string | null
  - **total_marks***: integer | null
  - **pass_mark**: integer | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/assessments/{assessment_id}
**Summary**: Get an assessment by ID

### Parameters
- **assessment_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **module_id***: string | null
- **title***: string | null
- **total_marks***: integer | null
- **pass_mark**: integer | null

---

## PATCH /api/v1/assessments/{assessment_id}
**Summary**: Update an assessment (staff only)

### Parameters
- **assessment_id*** (path): string

### Request Body

- **title**: string | null
- **total_marks**: integer | null
- **pass_mark**: integer | null
- **module_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **workshop_id***: string | null
- **module_id***: string | null
- **title***: string | null
- **total_marks***: integer | null
- **pass_mark**: integer | null

---

## DELETE /api/v1/assessments/{assessment_id}
**Summary**: Delete an assessment (staff only)

### Parameters
- **assessment_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/assessments/{assessment_id}/questions
**Summary**: Add a question to an assessment (staff only)

### Parameters
- **assessment_id*** (path): string

### Request Body

- **assessment_id***: string
- **text***: string
- **type***: string
- **marks**: integer
- **options**: Array of [- **id***: string
  - **text***: string
  - **is_correct**: boolean]

### Response: 200/201 (JSON)

- **id***: string
- **assessment_id***: string | null
- **text***: string | null
- **type***: string | null
- **marks***: integer | null
- **options**: Array of [- **id***: string
  - **text***: string
  - **is_correct**: boolean]

---

## GET /api/v1/assessments/{assessment_id}/questions
**Summary**: List questions for an assessment (staff sees is_correct)

### Parameters
- **assessment_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **assessment_id***: string | null
  - **text***: string | null
  - **type***: string | null
  - **marks***: integer | null
  - **options**: Array of [- **id***: string
    - **text***: string
    - **is_correct**: boolean]]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## PATCH /api/v1/questions/{question_id}
**Summary**: Update a question (staff only)

### Parameters
- **question_id*** (path): string

### Request Body

- **text**: string | null
- **type**: string | null
- **marks**: integer | null
- **options**: Array of [- **id***: string
  - **text***: string
  - **is_correct**: boolean] | null

### Response: 200/201 (JSON)

- **id***: string
- **assessment_id***: string | null
- **text***: string | null
- **type***: string | null
- **marks***: integer | null
- **options**: Array of [- **id***: string
  - **text***: string
  - **is_correct**: boolean]

---

## DELETE /api/v1/questions/{question_id}
**Summary**: Delete a question (staff only)

### Parameters
- **question_id*** (path): string

### Response: No Content or File

---

## POST /api/v1/tests/{assessment_id}/start
**Summary**: Start a test — creates a blank submission and returns questions (no correct answers)

### Parameters
- **assessment_id*** (path): string

### Response: 200/201 (JSON)

- **submission_id***: string
- **assessment_id***: string
- **title***: string
- **total_marks***: integer
- **questions***: Array of [- **id***: string
  - **assessment_id***: string | null
  - **text***: string | null
  - **type***: string | null
  - **marks***: integer | null
  - **options**: Array of [- **id***: string
    - **text***: string]]

---

## POST /api/v1/tests/{assessment_id}/submit
**Summary**: Submit test answers — auto-grades MCQ/MSQ, persists score and pass/fail

### Parameters
- **assessment_id*** (path): string
- **submission_id*** (query): string

### Response: 200/201 (JSON)

- **submission_id***: string
- **score***: integer
- **total_marks***: integer
- **percentage***: number
- **pass_fail***: boolean
- **per_question***: Array of [dict]

---

## POST /api/v1/submissions/{submission_id}/answers
**Summary**: Append or replace answers in a submission (student: own only)

### Parameters
- **submission_id*** (path): string

### Request Body

- **answers***: Array of [- **question_id***: string
  - **selected_option_ids**: Array of [string]]

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **assessment_id***: string | null
- **score***: integer | null
- **percentage***: integer | null
- **pass_fail**: boolean | null
- **answers**: Array of [- **question_id***: string
  - **selected_option_ids**: Array of [string]]
- **submitted_at***: string | null

---

## GET /api/v1/submissions/{submission_id}/result
**Summary**: Get graded result of a submission

### Parameters
- **submission_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **assessment_id***: string | null
- **score***: integer | null
- **percentage***: integer | null
- **pass_fail**: boolean | null
- **answers**: Array of [- **question_id***: string
  - **selected_option_ids**: Array of [string]]
- **submitted_at***: string | null

---

## GET /api/v1/submissions/student/{student_id}
**Summary**: List all submissions for a student

### Parameters
- **student_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **assessment_id***: string | null
  - **score***: integer | null
  - **percentage***: integer | null
  - **pass_fail**: boolean | null
  - **answers**: Array of [- **question_id***: string
    - **selected_option_ids**: Array of [string]]
  - **submitted_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/submissions/assessment/{assessment_id}
**Summary**: List all submissions for an assessment (staff only)

### Parameters
- **assessment_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **assessment_id***: string | null
  - **score***: integer | null
  - **percentage***: integer | null
  - **pass_fail**: boolean | null
  - **answers**: Array of [- **question_id***: string
    - **selected_option_ids**: Array of [string]]
  - **submitted_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## POST /api/v1/certificates/generate
**Summary**: Generate a certificate for a student (staff only)

### Request Body

- **student_id***: string
- **workshop_id***: string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **issue_date***: string | null
- **verification_code***: string | null
- **qr_url**: string | null
- **pdf_path**: string | null

---

## GET /api/v1/certificates/{certificate_id}
**Summary**: Fetch a certificate by ID

### Parameters
- **certificate_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **issue_date***: string | null
- **verification_code***: string | null
- **qr_url**: string | null
- **pdf_path**: string | null

---

## GET /api/v1/certificates/student/{student_id}
**Summary**: List all certificates for a student

### Parameters
- **student_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **workshop_id***: string | null
  - **issue_date***: string | null
  - **verification_code***: string | null
  - **qr_url**: string | null
  - **pdf_path**: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/certificates/verify/{verification_code}
**Summary**: Publicly verify a certificate by its verification code (no auth required)

### Parameters
- **verification_code*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **workshop_id***: string | null
- **issue_date***: string | null
- **verification_code***: string | null
- **qr_url**: string | null
- **pdf_path**: string | null

---

## POST /api/v1/fees/plans
**Summary**: Create a fee plan (admin / institution_admin only)

### Request Body

- **name***: string
- **amount***: integer
- **billing_cycle***: string

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **amount***: integer | null
- **billing_cycle***: string | null

---

## GET /api/v1/fees/plans
**Summary**: List all fee plans

### Parameters
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **name***: string | null
  - **amount***: integer | null
  - **billing_cycle***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/fees/plans/{plan_id}
**Summary**: Get a fee plan by ID

### Parameters
- **plan_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **amount***: integer | null
- **billing_cycle***: string | null

---

## PATCH /api/v1/fees/plans/{plan_id}
**Summary**: Update a fee plan (admin / institution_admin only)

### Parameters
- **plan_id*** (path): string

### Request Body

- **name**: string | null
- **amount**: integer | null
- **billing_cycle**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **name***: string | null
- **amount***: integer | null
- **billing_cycle***: string | null

---

## POST /api/v1/fees/assign
**Summary**: Assign a fee plan to a student

### Request Body

- **student_id***: string
- **fee_plan_id***: string
- **initial_balance**: integer

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **fee_plan_id***: string | null
- **balance***: integer | null
- **fee_plan**: 
  - **id***: string
  - **name***: string | null
  - **amount***: integer | null
  - **billing_cycle***: string | null | null

---

## GET /api/v1/fees/student/{student_id}
**Summary**: Get fee records for a student (with fee plan detail)

### Parameters
- **student_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **fee_plan_id***: string | null
  - **balance***: integer | null
  - **fee_plan**: 
    - **id***: string
    - **name***: string | null
    - **amount***: integer | null
    - **billing_cycle***: string | null | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## GET /api/v1/fees/{student_fee_id}
**Summary**: Get a specific student fee record

### Parameters
- **student_fee_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **fee_plan_id***: string | null
- **balance***: integer | null
- **fee_plan**: 
  - **id***: string
  - **name***: string | null
  - **amount***: integer | null
  - **billing_cycle***: string | null | null

---

## POST /api/v1/payments/
**Summary**: Record a payment (staff only); optionally credits a student fee balance

### Request Body

- **student_id***: string
- **amount***: integer
- **method***: string
- **reference**: string | null
- **student_fee_id**: string | null

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **amount***: integer | null
- **method***: string | null
- **reference***: string | null
- **created_at***: string | null

---

## GET /api/v1/payments/{payment_id}
**Summary**: Get a payment record by ID (staff only)

### Parameters
- **payment_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **student_id***: string | null
- **amount***: integer | null
- **method***: string | null
- **reference***: string | null
- **created_at***: string | null

---

## GET /api/v1/payments/student/{student_id}
**Summary**: List payment history for a student (newest first)

### Parameters
- **student_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **student_id***: string | null
  - **amount***: integer | null
  - **method***: string | null
  - **reference***: string | null
  - **created_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## POST /api/v1/students/bulk-upload
**Summary**: Upload a CSV to bulk-create student accounts (admin / institution_admin only)

### Request Body

- **file***: string

### Response: 200/201 (JSON)

- **created***: integer
- **skipped***: integer
- **errors***: Array of [dict]

---

## POST /api/v1/enrollments/bulk
**Summary**: Bulk enrol students in workshops (staff only)

### Request Body

- **enrollments***: Array of [- **student_id***: string
  - **workshop_id***: string]

### Response: 200/201 (JSON)

- **created***: integer
- **errors***: Array of [dict]

---

## POST /api/v1/attendance/bulk
**Summary**: Bulk mark attendance for a session (staff only)

### Request Body

- **records***: Array of [- **session_id***: string
  - **student_id***: string
  - **status**: string]

### Response: 200/201 (JSON)

- **created***: integer
- **errors***: Array of [dict]

---

## GET /api/v1/analytics/student/{student_id}
**Summary**: Get performance trends, average scores, and attendance % for a student

### Parameters
- **student_id*** (path): string

### Response: 200/201 (JSON)
dict

---

## GET /api/v1/analytics/attendance/{student_id}
**Summary**: Get detailed chronological attendance records for a student

### Parameters
- **student_id*** (path): string

### Response: 200/201 (JSON)
dict

---

## GET /api/v1/analytics/workshop/{workshop_id}
**Summary**: Get cohort-level averages and pass rates for a workshop (staff only)

### Parameters
- **workshop_id*** (path): string

### Response: 200/201 (JSON)
dict

---

## POST /api/v1/notifications/send
**Summary**: Send a notification to multiple users concurrently (staff only)

### Request Body

- **user_ids***: Array of [string]
- **message***: string
- **notification_type**: string

### Response: 200/201 (JSON)
Array of [- **id***: string
- **user_id***: string | null
- **message***: string | null
- **status***: string | null
- **notification_type***: string | null
- **created_at***: string | null]

---

## GET /api/v1/notifications/{user_id}
**Summary**: List all notifications for a user (newest first)

### Parameters
- **user_id*** (path): string
- **offset** (query): integer
- **limit** (query): integer

### Response: 200/201 (JSON)

- **items***: Array of [- **id***: string
  - **user_id***: string | null
  - **message***: string | null
  - **status***: string | null
  - **notification_type***: string | null
  - **created_at***: string | null]
- **total***: integer
- **offset***: integer
- **limit***: integer

---

## PATCH /api/v1/notifications/{notification_id}/read
**Summary**: Mark a notification as read

### Parameters
- **notification_id*** (path): string

### Response: 200/201 (JSON)

- **id***: string
- **user_id***: string | null
- **message***: string | null
- **status***: string | null
- **notification_type***: string | null
- **created_at***: string | null

---

## DELETE /api/v1/notifications/{notification_id}
**Summary**: Delete a notification

### Parameters
- **notification_id*** (path): string

### Response: No Content or File

---

## GET /
**Summary**: Health

### Response: 200/201 (JSON)
dict

---
