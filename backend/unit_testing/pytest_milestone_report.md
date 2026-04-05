# Pytest Milestone Report

- Generated at: `2026-04-05 06:20:18`
- Test scope: `backend/unit_testing/test_*.py`
- Summary: **Passed=38**, **Failed/Error=1**, **Skipped=0**, **Not captured=0**

## Test Case Matrix (Expected vs Actual)

| Test Case | Code Reference | Expected Output | Actual Output |
|---|---|---|---|
| `unit_testing/test_educator.py::test_educator_dashboard_stats` | `unit_testing/test_educator.py:203` | `assert response.status_code == 200`<br>`assert payload["assigned_workshops"] >= 1`<br>`assert payload["active_assessments"] >= 1` | PASSED |
| `unit_testing/test_educator.py::test_educator_workshop_list_is_scoped` | `unit_testing/test_educator.py:214` | `assert response.status_code == 200`<br>`assert "workshop-own" in ids`<br>`assert "workshop-other" not in ids` | PASSED |
| `unit_testing/test_educator.py::test_educator_can_view_assessments_and_submissions` | `unit_testing/test_educator.py:225` | `assert assessments_response.status_code == 200`<br>`assert assessments_response.json()["total"] >= 1`<br>`assert submissions_response.status_code == 200`<br>`assert submissions_response.json()["total"] >= 1` | PASSED |
| `unit_testing/test_educator.py::test_educator_material_upload_and_delete` | `unit_testing/test_educator.py:238` | `assert upload_response.status_code == 200`<br>`assert uploaded is not None`<br>`assert download_response.status_code == 200`<br>`assert "/media/modules/module-1/" in download_response.json()["download_url"]`<br>`assert delete_response.status_code == 200`<br>`assert uploaded["id"] not in remaining_ids` | PASSED |
| `unit_testing/test_educator.py::test_educator_can_fetch_workshop_analytics` | `unit_testing/test_educator.py:261` | `assert response.status_code == 200`<br>`assert payload["workshop_id"] == "workshop-own"`<br>`assert "assessment" in payload`<br>`assert "pass_rate_percentage" in payload["assessment"]` | PASSED |
| `unit_testing/test_educator.py::test_educator_notifications_success` | `unit_testing/test_educator.py:273` | `assert response.status_code == 200`<br>`assert response.json()["total"] >= 1` | PASSED |
| `unit_testing/test_educator.py::test_educator_can_view_review_and_dispatch_parent_message` | `unit_testing/test_educator.py:282` | `assert review.status_code == 200`<br>`assert review_payload["submission_id"] == "submission-graded"`<br>`assert len(review_payload["questions"]) >= 1`<br>`assert message.status_code == 200`<br>`assert message.json()["accepted"] == 1`<br>`assert assessment_lb.status_code == 200`<br>`assert assessment_drilldown.status_code == 200`<br>`assert assessment_drilldown.json()["student_id"] == "student-1"`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_educator.py::test_educator_can_grade_pending_submission` | `unit_testing/test_educator.py:315` | `assert response.status_code == 200`<br>`assert payload["id"] == "submission-1"`<br>`assert payload["pass_fail"] is False`<br>`assert repeat.status_code == 409` | PASSED |
| `unit_testing/test_educator.py::test_educator_workshop_educator_profile_contract` | `unit_testing/test_educator.py:329` | `assert own_profile.status_code == 200`<br>`assert payload["workshop_id"] == "workshop-own"`<br>`assert payload["email"] == "educator@vidyasetu.edu"`<br>`assert cross_institution.status_code == 403` | PASSED |
| `unit_testing/test_educator.py::test_educator_certificate_recommend_and_download` | `unit_testing/test_educator.py:343` | `assert recommend.status_code == 200`<br>`assert recommend.json()["accepted"] >= 1`<br>`assert download.status_code == 200`<br>`assert "/media/certificates/certificate-1.pdf" in download.json()["download_url"]` | PASSED |
| `unit_testing/test_educator.py::test_educator_performance_export_available` | `unit_testing/test_educator.py:359` | `assert response.status_code == 200`<br>`assert payload["file_type"] == "csv"`<br>`assert "/media/exports/" in payload["download_url"]` | PASSED |
| `unit_testing/test_educator.py::test_educator_forbidden_admin_and_delete_routes` | `unit_testing/test_educator.py:370` | `assert admin_dashboard.status_code == 403`<br>`assert delete_workshop.status_code == 403` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_stats` | `unit_testing/test_institutional_admin.py:202` | `assert response.status_code == 200`<br>`assert payload["assigned_workshops"] >= 1`<br>`assert "pending_submissions" in payload` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_workshop_scope_and_create` | `unit_testing/test_institutional_admin.py:213` | `assert list_response.status_code == 200`<br>`assert "workshop-own" in returned_ids`<br>`assert "workshop-other" not in returned_ids`<br>`assert create_response.status_code == 201`<br>`assert create_response.json()["institution_id"] == "inst-1"` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_update_other_institution_workshop` | `unit_testing/test_institutional_admin.py:231` | `assert response.status_code == 403` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_users_list_is_scoped` | `unit_testing/test_institutional_admin.py:239` | `assert response.status_code == 200`<br>`assert all(item["institution_id"] == "inst-1" for item in users)` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_can_fetch_student_enrollments` | `unit_testing/test_institutional_admin.py:249` | `assert response.status_code == 200`<br>`assert response.json()["total"] >= 1` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_can_create_approval_request` | `unit_testing/test_institutional_admin.py:258` | `assert response.status_code == 201`<br>`assert response.json()["status"] == "pending"` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_aggregate_and_leaderboards` | `unit_testing/test_institutional_admin.py:270` | `assert aggregate.status_code == 200`<br>`assert "kpis" in payload`<br>`assert "alerts" in payload`<br>`assert "attendance_trend" in payload`<br>`assert assessment_lb.status_code == 200`<br>`assert assessment_lb.json()["assessment_id"] == "assessment-1"`<br>`assert workshop_lb.status_code == 200`<br>`assert workshop_lb.json()["workshop_id"] == "workshop-own"`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report` | `unit_testing/test_institutional_admin.py:298` | `assert students.status_code == 200`<br>`assert payload["total"] >= 1`<br>`assert any(item["id"] == "student-1" for item in payload["items"])`<br>`assert attendance.status_code == 200`<br>`assert attendance_payload["total"] >= 1`<br>`assert any(item["student"] == "Student One" for item in attendance_payload["rows"])` | FAILED<br>`E   assert 0 >= 1` |
| `unit_testing/test_institutional_admin.py::test_institution_admin_parent_message_dispatch` | `unit_testing/test_institutional_admin.py:315` | `assert response.status_code == 200`<br>`assert response.json()["accepted"] == 1` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_bulk_and_export_endpoints` | `unit_testing/test_institutional_admin.py:331` | `assert bulk_action.status_code == 200`<br>`assert payload["requested_students"] == 1`<br>`assert payload["updated_enrollments"] >= 1`<br>`assert students.status_code == 200`<br>`assert student_row["status"] == "Inactive"`<br>`assert students_export.status_code == 200`<br>`assert "/media/exports/" in students_export.json()["download_url"]`<br>`assert attendance_export.status_code == 200`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_parent_contact_lookup` | `unit_testing/test_institutional_admin.py:361` | `assert response.status_code == 200`<br>`assert payload["total"] == 1`<br>`assert payload["items"][0]["student_id"] == "student-1"`<br>`assert payload["items"][0]["parent_email"] == "parent1@example.com"` | PASSED |
| `unit_testing/test_institutional_admin.py::test_institution_admin_profile_metadata_update_self_only` | `unit_testing/test_institutional_admin.py:373` | `assert update_self.status_code == 200`<br>`assert payload["bio"] == "Leads institutional operations."`<br>`assert payload["department"] == "Administration"`<br>`assert payload["institution_admin_code"] == "IITD-SA"`<br>`assert update_other.status_code == 403` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_dashboard_stats_success` | `unit_testing/test_platform_admin.py:178` | `assert response.status_code == 200`<br>`assert payload["total_institutions"] >= 1`<br>`assert payload["total_workshops"] >= 1`<br>`assert payload["total_students"] >= 1` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_dashboard_forbidden_for_non_admin` | `unit_testing/test_platform_admin.py:190` | `assert response.status_code == 403` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_workshop_crud` | `unit_testing/test_platform_admin.py:198` | `assert create_response.status_code == 201`<br>`assert patch_response.status_code == 200`<br>`assert patch_response.json()["title"] == "Renamed Workshop"`<br>`assert delete_response.status_code == 204` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve` | `unit_testing/test_platform_admin.py:221` | `assert list_response.status_code == 200`<br>`assert "approval-1" in request_ids`<br>`assert approve_response.status_code == 200`<br>`assert approve_response.json()["status"] == "approved"` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_salary_pay_and_list` | `unit_testing/test_platform_admin.py:235` | `assert pay_response.status_code == 201`<br>`assert pay_response.json()["amount"] == 62000`<br>`assert list_response.status_code == 200`<br>`assert any(item["month"] == "2026-04" for item in list_response.json()["items"])` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_users_and_institutions_endpoints` | `unit_testing/test_platform_admin.py:251` | `assert users_response.status_code == 200`<br>`assert users_response.json()["total"] >= 3`<br>`assert institutions_response.status_code == 200`<br>`assert any(item["id"] == "inst-1" for item in institutions_response.json())` | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_new_analytics_endpoints` | `unit_testing/test_platform_admin.py:264` | `assert assessment_lb.status_code == 200`<br>`assert assessment_lb.json()["assessment_id"] == "assessment-1"`<br>`assert len(assessment_lb.json()["entries"]) >= 1`<br>`assert workshop_lb.status_code == 200`<br>`assert workshop_lb.json()["workshop_id"] == "workshop-1"`<br>`assert admin_insights.status_code == 200`<br>`assert "weekly_activity" in payload`<br>`assert len(payload["weekly_activity"]) == 7`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_platform_admin.py::test_admin_parent_communication_dispatch` | `unit_testing/test_platform_admin.py:308` | `assert response.status_code == 200`<br>`assert payload["accepted"] == 1`<br>`assert payload["failed"] == 0` | PASSED |
| `unit_testing/test_student.py::test_student_auth_register_and_login` | `unit_testing/test_student.py:177` | `assert register_response.status_code == 201`<br>`assert login_response.status_code == 200`<br>`assert "access_token" in login_response.json()`<br>`assert "refresh_token" in login_response.json()` | PASSED |
| `unit_testing/test_student.py::test_student_dashboard_and_analytics` | `unit_testing/test_student.py:196` | `assert dashboard.status_code == 200`<br>`assert "enrolled_workshops" in dashboard.json()`<br>`assert analytics.status_code == 200`<br>`assert payload["student_id"] == "student-1"`<br>`assert "assessment" in payload`<br>`assert "avg_percentage" in payload["assessment"]`<br>`assert "score_trend" in payload["assessment"]`<br>`assert isinstance(payload["assessment"]["score_trend"], list)`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_student.py::test_student_workshops_and_enrollments` | `unit_testing/test_student.py:218` | `assert workshops.status_code == 200`<br>`assert workshops.json()["total"] >= 1`<br>`assert enrollments.status_code == 200`<br>`assert enrollments.json()["total"] >= 1`<br>`assert forbidden_enroll.status_code == 403` | PASSED |
| `unit_testing/test_student.py::test_student_attempt_start_save_submit_flow` | `unit_testing/test_student.py:235` | `assert start_response.status_code == 201`<br>`assert len(start_payload["questions"]) >= 2`<br>`assert save_answers.status_code == 200`<br>`assert submit.status_code == 200`<br>`assert submit.json()["score"] == 20`<br>`assert submit.json()["pass_fail"] is True`<br>`assert re_submit.status_code == 409` | PASSED |
| `unit_testing/test_student.py::test_student_certificates_notifications_and_profile` | `unit_testing/test_student.py:267` | `assert certificates.status_code == 200`<br>`assert certificates.json()["total"] >= 1`<br>`assert verify.status_code == 200`<br>`assert notifications.status_code == 200`<br>`assert notifications.json()["total"] >= 1`<br>`assert mark_read.status_code == 200`<br>`assert mark_read.json()["status"] == "read"`<br>`assert delete_notification.status_code == 204`<br>... (additional assertions in code) | PASSED |
| `unit_testing/test_student.py::test_student_forbidden_from_other_student_data` | `unit_testing/test_student.py:319` | `assert other_profile.status_code == 403`<br>`assert other_dashboard.status_code == 403`<br>`assert other_analytics.status_code == 403`<br>`assert other_upload.status_code == 403` | PASSED |
| `unit_testing/test_student.py::test_student_leaderboard_access_and_staff_only_guards` | `unit_testing/test_student.py:339` | `assert assessment_lb.status_code == 200`<br>`assert assessment_lb.json()["assessment_id"] == "assessment-1"`<br>`assert workshop_lb.status_code == 200`<br>`assert workshop_lb.json()["workshop_id"] == "workshop-1"`<br>`assert assessment_drilldown.status_code == 200`<br>`assert assessment_drilldown.json()["student_id"] == "student-1"`<br>`assert workshop_drilldown.status_code == 200`<br>`assert workshop_drilldown.json()["context_type"] == "workshop"`<br>... (additional assertions in code) | PASSED |

## Code Snippets

### unit_testing/test_educator.py::test_educator_dashboard_stats
- Source: `unit_testing/test_educator.py:203`
- Status: **PASSED**

```python
def test_educator_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert payload["active_assessments"] >= 1
```

### unit_testing/test_educator.py::test_educator_workshop_list_is_scoped
- Source: `unit_testing/test_educator.py:214`
- Status: **PASSED**

```python
def test_educator_workshop_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/workshops/")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert "workshop-own" in ids
    assert "workshop-other" not in ids
```

### unit_testing/test_educator.py::test_educator_can_view_assessments_and_submissions
- Source: `unit_testing/test_educator.py:225`
- Status: **PASSED**

```python
def test_educator_can_view_assessments_and_submissions(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assessments_response = client.get("/api/v1/assessments/workshop/workshop-own")
    assert assessments_response.status_code == 200
    assert assessments_response.json()["total"] >= 1

    submissions_response = client.get("/api/v1/submissions/assessment/assessment-1")
    assert submissions_response.status_code == 200
    assert submissions_response.json()["total"] >= 1
```

### unit_testing/test_educator.py::test_educator_material_upload_and_delete
- Source: `unit_testing/test_educator.py:238`
- Status: **PASSED**

```python
def test_educator_material_upload_and_delete(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    upload_response = client.post(
        "/api/v1/modules/module-1/materials/upload",
        files={"file": ("lecture-notes.txt", b"hello materials", "text/plain")},
    )
    assert upload_response.status_code == 200
    materials = upload_response.json()["materials"]
    uploaded = next((item for item in materials if item["title"] == "lecture-notes.txt"), None)
    assert uploaded is not None

    download_response = client.get(f"/api/v1/materials/module-1/{uploaded['id']}/download")
    assert download_response.status_code == 200
    assert "/media/modules/module-1/" in download_response.json()["download_url"]

    delete_response = client.delete(f"/api/v1/materials/module-1/{uploaded['id']}")
    ...
```

### unit_testing/test_educator.py::test_educator_can_fetch_workshop_analytics
- Source: `unit_testing/test_educator.py:261`
- Status: **PASSED**

```python
def test_educator_can_fetch_workshop_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/workshop/workshop-own")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workshop_id"] == "workshop-own"
    assert "assessment" in payload
    assert "pass_rate_percentage" in payload["assessment"]
```

### unit_testing/test_educator.py::test_educator_notifications_success
- Source: `unit_testing/test_educator.py:273`
- Status: **PASSED**

```python
def test_educator_notifications_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/educator-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
```

### unit_testing/test_educator.py::test_educator_can_view_review_and_dispatch_parent_message
- Source: `unit_testing/test_educator.py:282`
- Status: **PASSED**

```python
def test_educator_can_view_review_and_dispatch_parent_message(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    review = client.get("/api/v1/submissions/submission-graded/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["submission_id"] == "submission-graded"
    assert len(review_payload["questions"]) >= 1

    message = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Submission Reviewed",
            "body": "Please check updated breakdown.",
        },
    )
    ...
```

### unit_testing/test_educator.py::test_educator_can_grade_pending_submission
- Source: `unit_testing/test_educator.py:315`
- Status: **PASSED**

```python
def test_educator_can_grade_pending_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.post("/api/v1/submissions/submission-1/grade")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "submission-1"
    assert payload["pass_fail"] is False

    repeat = client.post("/api/v1/submissions/submission-1/grade")
    assert repeat.status_code == 409
```

### unit_testing/test_educator.py::test_educator_workshop_educator_profile_contract
- Source: `unit_testing/test_educator.py:329`
- Status: **PASSED**

```python
def test_educator_workshop_educator_profile_contract(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    own_profile = client.get("/api/v1/workshops/workshop-own/educator-profile")
    assert own_profile.status_code == 200
    payload = own_profile.json()
    assert payload["workshop_id"] == "workshop-own"
    assert payload["email"] == "educator@vidyasetu.edu"

    cross_institution = client.get("/api/v1/workshops/workshop-other/educator-profile")
    assert cross_institution.status_code == 403
```

### unit_testing/test_educator.py::test_educator_certificate_recommend_and_download
- Source: `unit_testing/test_educator.py:343`
- Status: **PASSED**

```python
def test_educator_certificate_recommend_and_download(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    recommend = client.post(
        "/api/v1/certificates/recommend",
        json={"student_id": "student-1", "workshop_id": "workshop-own", "note": "Ready for certificate."},
    )
    assert recommend.status_code == 200
    assert recommend.json()["accepted"] >= 1

    download = client.get("/api/v1/certificates/certificate-1/download")
    assert download.status_code == 200
    assert "/media/certificates/certificate-1.pdf" in download.json()["download_url"]
```

### unit_testing/test_educator.py::test_educator_performance_export_available
- Source: `unit_testing/test_educator.py:359`
- Status: **PASSED**

```python
def test_educator_performance_export_available(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/reports/performance/export")
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_type"] == "csv"
    assert "/media/exports/" in payload["download_url"]
```

### unit_testing/test_educator.py::test_educator_forbidden_admin_and_delete_routes
- Source: `unit_testing/test_educator.py:370`
- Status: **PASSED**

```python
def test_educator_forbidden_admin_and_delete_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    admin_dashboard = client.get("/api/v1/dashboard/admin")
    assert admin_dashboard.status_code == 403

    delete_workshop = client.delete("/api/v1/workshops/workshop-own")
    assert delete_workshop.status_code == 403
```

### unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_stats
- Source: `unit_testing/test_institutional_admin.py:202`
- Status: **PASSED**

```python
def test_institution_admin_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert "pending_submissions" in payload
```

### unit_testing/test_institutional_admin.py::test_institution_admin_workshop_scope_and_create
- Source: `unit_testing/test_institutional_admin.py:213`
- Status: **PASSED**

```python
def test_institution_admin_workshop_scope_and_create(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    list_response = client.get("/api/v1/workshops/")
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.json()["items"]}
    assert "workshop-own" in returned_ids
    assert "workshop-other" not in returned_ids

    create_response = client.post(
        "/api/v1/workshops/",
        json={"title": "Created by Institution Admin", "description": "Scoped create"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["institution_id"] == "inst-1"
```

### unit_testing/test_institutional_admin.py::test_institution_admin_cannot_update_other_institution_workshop
- Source: `unit_testing/test_institutional_admin.py:231`
- Status: **PASSED**

```python
def test_institution_admin_cannot_update_other_institution_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.patch("/api/v1/workshops/workshop-other", json={"title": "Illegal update"})
    assert response.status_code == 403
```

### unit_testing/test_institutional_admin.py::test_institution_admin_users_list_is_scoped
- Source: `unit_testing/test_institutional_admin.py:239`
- Status: **PASSED**

```python
def test_institution_admin_users_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/users/?limit=200")
    assert response.status_code == 200
    users = response.json()["items"]
    assert all(item["institution_id"] == "inst-1" for item in users)
```

### unit_testing/test_institutional_admin.py::test_institution_admin_can_fetch_student_enrollments
- Source: `unit_testing/test_institutional_admin.py:249`
- Status: **PASSED**

```python
def test_institution_admin_can_fetch_student_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/enrollments/student/student-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
```

### unit_testing/test_institutional_admin.py::test_institution_admin_can_create_approval_request
- Source: `unit_testing/test_institutional_admin.py:258`
- Status: **PASSED**

```python
def test_institution_admin_can_create_approval_request(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/approvals/requests",
        json={"request_type": "delete_student", "payload": {"user_id": "student-1"}},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
```

### unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_aggregate_and_leaderboards
- Source: `unit_testing/test_institutional_admin.py:270`
- Status: **PASSED**

```python
def test_institution_admin_dashboard_aggregate_and_leaderboards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    aggregate = client.get("/api/v1/analytics/institution/dashboard")
    assert aggregate.status_code == 200
    payload = aggregate.json()
    assert "kpis" in payload
    assert "alerts" in payload
    assert "attendance_trend" in payload

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-own"
    ...
```

### unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report
- Source: `unit_testing/test_institutional_admin.py:298`
- Status: **FAILED**
- Failure detail: `E   assert 0 >= 1`

```python
def test_institution_admin_student_roster_and_attendance_report(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    payload = students.json()
    assert payload["total"] >= 1
    assert any(item["id"] == "student-1" for item in payload["items"])

    attendance = client.get("/api/v1/analytics/institution/attendance-report")
    assert attendance.status_code == 200
    attendance_payload = attendance.json()
    assert attendance_payload["total"] >= 1
    assert any(item["student"] == "Student One" for item in attendance_payload["rows"])
```

### unit_testing/test_institutional_admin.py::test_institution_admin_parent_message_dispatch
- Source: `unit_testing/test_institutional_admin.py:315`
- Status: **PASSED**

```python
def test_institution_admin_parent_message_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Progress Update",
            "body": "Please review the latest grades.",
        },
    )
    assert response.status_code == 200
    assert response.json()["accepted"] == 1
```

### unit_testing/test_institutional_admin.py::test_institution_admin_bulk_and_export_endpoints
- Source: `unit_testing/test_institutional_admin.py:331`
- Status: **PASSED**

```python
def test_institution_admin_bulk_and_export_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    bulk_action = client.post(
        "/api/v1/analytics/institution/students/bulk-action",
        json={"student_ids": ["student-1"], "action": "set_inactive"},
    )
    assert bulk_action.status_code == 200
    payload = bulk_action.json()
    assert payload["requested_students"] == 1
    assert payload["updated_enrollments"] >= 1

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    student_row = next(item for item in students.json()["items"] if item["id"] == "student-1")
    assert student_row["status"] == "Inactive"

    ...
```

### unit_testing/test_institutional_admin.py::test_institution_admin_parent_contact_lookup
- Source: `unit_testing/test_institutional_admin.py:361`
- Status: **PASSED**

```python
def test_institution_admin_parent_contact_lookup(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/communication/parent-contacts?student_ids=student-1&student_ids=student-2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["student_id"] == "student-1"
    assert payload["items"][0]["parent_email"] == "parent1@example.com"
```

### unit_testing/test_institutional_admin.py::test_institution_admin_profile_metadata_update_self_only
- Source: `unit_testing/test_institutional_admin.py:373`
- Status: **PASSED**

```python
def test_institution_admin_profile_metadata_update_self_only(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    update_self = client.patch(
        "/api/v1/users/inst-admin-1",
        json={
            "bio": "Leads institutional operations.",
            "department": "Administration",
            "institution_admin_name": "IIT Delhi South Campus",
            "institution_admin_address": "Hauz Khas, New Delhi",
            "institution_admin_code": "IITD-SA",
        },
    )
    assert update_self.status_code == 200
    payload = update_self.json()
    assert payload["bio"] == "Leads institutional operations."
    assert payload["department"] == "Administration"
    ...
```

### unit_testing/test_platform_admin.py::test_admin_dashboard_stats_success
- Source: `unit_testing/test_platform_admin.py:178`
- Status: **PASSED**

```python
def test_admin_dashboard_stats_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_institutions"] >= 1
    assert payload["total_workshops"] >= 1
    assert payload["total_students"] >= 1
```

### unit_testing/test_platform_admin.py::test_admin_dashboard_forbidden_for_non_admin
- Source: `unit_testing/test_platform_admin.py:190`
- Status: **PASSED**

```python
def test_admin_dashboard_forbidden_for_non_admin(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-inst-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 403
```

### unit_testing/test_platform_admin.py::test_admin_workshop_crud
- Source: `unit_testing/test_platform_admin.py:198`
- Status: **PASSED**

```python
def test_admin_workshop_crud(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    create_response = client.post(
        "/api/v1/workshops/",
        json={
            "title": "New Admin Workshop",
            "description": "Created by admin",
            "institution_id": "inst-1",
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    patch_response = client.patch(f"/api/v1/workshops/{created_id}", json={"title": "Renamed Workshop"})
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Renamed Workshop"
    ...
```

### unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve
- Source: `unit_testing/test_platform_admin.py:221`
- Status: **PASSED**

```python
def test_admin_approval_list_and_approve(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    list_response = client.get("/api/v1/approvals/requests")
    assert list_response.status_code == 200
    request_ids = [item["id"] for item in list_response.json()["items"]]
    assert "approval-1" in request_ids

    approve_response = client.post("/api/v1/approvals/requests/approval-1/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"
```

### unit_testing/test_platform_admin.py::test_admin_salary_pay_and_list
- Source: `unit_testing/test_platform_admin.py:235`
- Status: **PASSED**

```python
def test_admin_salary_pay_and_list(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    pay_response = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "user-inst-admin", "month": "2026-04", "amount": 62000},
    )
    assert pay_response.status_code == 201
    assert pay_response.json()["amount"] == 62000

    list_response = client.get("/api/v1/salaries/?month=2026-04")
    assert list_response.status_code == 200
    assert any(item["month"] == "2026-04" for item in list_response.json()["items"])
```

### unit_testing/test_platform_admin.py::test_admin_users_and_institutions_endpoints
- Source: `unit_testing/test_platform_admin.py:251`
- Status: **PASSED**

```python
def test_admin_users_and_institutions_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    users_response = client.get("/api/v1/users/?limit=50")
    assert users_response.status_code == 200
    assert users_response.json()["total"] >= 3

    institutions_response = client.get("/api/v1/institutions/")
    assert institutions_response.status_code == 200
    assert any(item["id"] == "inst-1" for item in institutions_response.json())
```

### unit_testing/test_platform_admin.py::test_admin_new_analytics_endpoints
- Source: `unit_testing/test_platform_admin.py:264`
- Status: **PASSED**

```python
def test_admin_new_analytics_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"
    assert len(assessment_lb.json()["entries"]) >= 1

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    admin_insights = client.get("/api/v1/analytics/admin/insights")
    assert admin_insights.status_code == 200
    payload = admin_insights.json()
    assert "weekly_activity" in payload
    assert len(payload["weekly_activity"]) == 7
    ...
```

### unit_testing/test_platform_admin.py::test_admin_parent_communication_dispatch
- Source: `unit_testing/test_platform_admin.py:308`
- Status: **PASSED**

```python
def test_admin_parent_communication_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["user-student"],
            "subject": "Attendance Follow-up",
            "body": "Please connect with mentor.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] == 1
    assert payload["failed"] == 0
```

### unit_testing/test_student.py::test_student_auth_register_and_login
- Source: `unit_testing/test_student.py:177`
- Status: **PASSED**

```python
def test_student_auth_register_and_login(client_and_state):
    client, _ = client_and_state

    register_response = client.post(
        "/api/v1/auth/register",
        json={"name": "New Student", "email": "newstudent@vidyasetu.edu",
              "password": "secret123", "role": "student"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "newstudent@vidyasetu.edu", "password": "secret123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()
```

### unit_testing/test_student.py::test_student_dashboard_and_analytics
- Source: `unit_testing/test_student.py:196`
- Status: **PASSED**

```python
def test_student_dashboard_and_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    dashboard = client.get("/api/v1/dashboard/student/student-1")
    assert dashboard.status_code == 200
    assert "enrolled_workshops" in dashboard.json()

    analytics = client.get("/api/v1/analytics/student/student-1")
    assert analytics.status_code == 200
    payload = analytics.json()
    assert payload["student_id"] == "student-1"
    assert "assessment" in payload
    assert "avg_percentage" in payload["assessment"]
    assert "score_trend" in payload["assessment"]
    assert isinstance(payload["assessment"]["score_trend"], list)
    if payload["assessment"]["score_trend"]:
        first_point = payload["assessment"]["score_trend"][0]
    ...
```

### unit_testing/test_student.py::test_student_workshops_and_enrollments
- Source: `unit_testing/test_student.py:218`
- Status: **PASSED**

```python
def test_student_workshops_and_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    workshops = client.get("/api/v1/workshops/")
    assert workshops.status_code == 200
    assert workshops.json()["total"] >= 1

    enrollments = client.get("/api/v1/enrollments/student/student-1")
    assert enrollments.status_code == 200
    assert enrollments.json()["total"] >= 1

    forbidden_enroll = client.post(
        "/api/v1/enrollments/", json={"student_id": "student-2", "workshop_id": "workshop-1"})
    assert forbidden_enroll.status_code == 403
```

### unit_testing/test_student.py::test_student_attempt_start_save_submit_flow
- Source: `unit_testing/test_student.py:235`
- Status: **PASSED**

```python
def test_student_attempt_start_save_submit_flow(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    start_response = client.post("/api/v1/tests/assessment-1/start")
    assert start_response.status_code == 201
    start_payload = start_response.json()
    submission_id = start_payload["submission_id"]
    assert len(start_payload["questions"]) >= 2

    save_answers = client.post(
        f"/api/v1/submissions/{submission_id}/answers",
        json={
            "answers": [
                {"question_id": "question-1", "selected_option_ids": ["q1-a"]},
                {"question_id": "question-2", "selected_option_ids": ["q2-a"]},
            ]
        },
    ...
```

### unit_testing/test_student.py::test_student_certificates_notifications_and_profile
- Source: `unit_testing/test_student.py:267`
- Status: **PASSED**

```python
def test_student_certificates_notifications_and_profile(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    certificates = client.get("/api/v1/certificates/student/student-1")
    assert certificates.status_code == 200
    assert certificates.json()["total"] >= 1

    verify = client.get("/api/v1/certificates/verify/VERIFY-123")
    assert verify.status_code == 200

    notifications = client.get("/api/v1/notifications/student-1")
    assert notifications.status_code == 200
    assert notifications.json()["total"] >= 1

    first_notification_id = notifications.json()["items"][0]["id"]
    mark_read = client.patch(
        f"/api/v1/notifications/{first_notification_id}/read")
    ...
```

### unit_testing/test_student.py::test_student_forbidden_from_other_student_data
- Source: `unit_testing/test_student.py:319`
- Status: **PASSED**

```python
def test_student_forbidden_from_other_student_data(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    other_profile = client.get("/api/v1/users/student-2")
    assert other_profile.status_code == 403

    other_dashboard = client.get("/api/v1/dashboard/student/student-2")
    assert other_dashboard.status_code == 403

    other_analytics = client.get("/api/v1/analytics/student/student-2")
    assert other_analytics.status_code == 403

    other_upload = client.post(
        "/api/v1/users/student-2/profile-photo",
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    )
    assert other_upload.status_code == 403
```

### unit_testing/test_student.py::test_student_leaderboard_access_and_staff_only_guards
- Source: `unit_testing/test_student.py:339`
- Status: **PASSED**

```python
def test_student_leaderboard_access_and_staff_only_guards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    assessment_lb = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get(
        "/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    assessment_drilldown = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"
    ...
```

## Raw Pytest Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend
configfile: pyproject.toml
plugins: anyio-4.13.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 39 items

unit_testing/test_educator.py::test_educator_dashboard_stats PASSED      [  2%]
unit_testing/test_educator.py::test_educator_workshop_list_is_scoped PASSED [  5%]
unit_testing/test_educator.py::test_educator_can_view_assessments_and_submissions PASSED [  7%]
unit_testing/test_educator.py::test_educator_material_upload_and_delete PASSED [ 10%]
unit_testing/test_educator.py::test_educator_can_fetch_workshop_analytics PASSED [ 12%]
unit_testing/test_educator.py::test_educator_notifications_success PASSED [ 15%]
unit_testing/test_educator.py::test_educator_can_view_review_and_dispatch_parent_message PASSED [ 17%]
unit_testing/test_educator.py::test_educator_can_grade_pending_submission PASSED [ 20%]
unit_testing/test_educator.py::test_educator_workshop_educator_profile_contract PASSED [ 23%]
unit_testing/test_educator.py::test_educator_certificate_recommend_and_download PASSED [ 25%]
unit_testing/test_educator.py::test_educator_performance_export_available PASSED [ 28%]
unit_testing/test_educator.py::test_educator_forbidden_admin_and_delete_routes PASSED [ 30%]
unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_stats PASSED [ 33%]
unit_testing/test_institutional_admin.py::test_institution_admin_workshop_scope_and_create PASSED [ 35%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_update_other_institution_workshop PASSED [ 38%]
unit_testing/test_institutional_admin.py::test_institution_admin_users_list_is_scoped PASSED [ 41%]
unit_testing/test_institutional_admin.py::test_institution_admin_can_fetch_student_enrollments PASSED [ 43%]
unit_testing/test_institutional_admin.py::test_institution_admin_can_create_approval_request PASSED [ 46%]
unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_aggregate_and_leaderboards PASSED [ 48%]
unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report FAILED [ 51%]
unit_testing/test_institutional_admin.py::test_institution_admin_parent_message_dispatch PASSED [ 53%]
unit_testing/test_institutional_admin.py::test_institution_admin_bulk_and_export_endpoints PASSED [ 56%]
unit_testing/test_institutional_admin.py::test_institution_admin_parent_contact_lookup PASSED [ 58%]
unit_testing/test_institutional_admin.py::test_institution_admin_profile_metadata_update_self_only PASSED [ 61%]
unit_testing/test_platform_admin.py::test_admin_dashboard_stats_success PASSED [ 64%]
unit_testing/test_platform_admin.py::test_admin_dashboard_forbidden_for_non_admin PASSED [ 66%]
unit_testing/test_platform_admin.py::test_admin_workshop_crud PASSED     [ 69%]
unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve PASSED [ 71%]
unit_testing/test_platform_admin.py::test_admin_salary_pay_and_list PASSED [ 74%]
unit_testing/test_platform_admin.py::test_admin_users_and_institutions_endpoints PASSED [ 76%]
unit_testing/test_platform_admin.py::test_admin_new_analytics_endpoints PASSED [ 79%]
unit_testing/test_platform_admin.py::test_admin_parent_communication_dispatch PASSED [ 82%]
unit_testing/test_student.py::test_student_auth_register_and_login PASSED [ 84%]
unit_testing/test_student.py::test_student_dashboard_and_analytics PASSED [ 87%]
unit_testing/test_student.py::test_student_workshops_and_enrollments PASSED [ 89%]
unit_testing/test_student.py::test_student_attempt_start_save_submit_flow PASSED [ 92%]
unit_testing/test_student.py::test_student_certificates_notifications_and_profile PASSED [ 94%]
unit_testing/test_student.py::test_student_forbidden_from_other_student_data PASSED [ 97%]
unit_testing/test_student.py::test_student_leaderboard_access_and_staff_only_guards PASSED [100%]

================================== FAILURES ===================================
_________ test_institution_admin_student_roster_and_attendance_report _________
unit_testing\test_institutional_admin.py:311: in test_institution_admin_student_roster_and_attendance_report
    assert attendance_payload["total"] >= 1
E   assert 0 >= 1
============================== warnings summary ===============================
unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve
  E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\app\crud\crud_admin.py:51: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    req.resolved_at = datetime.utcnow()

.venv\Lib\site-packages\_pytest\cacheprovider.py:475
  E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\.venv\Lib\site-packages\_pytest\cacheprovider.py:475: PytestCacheWarning: could not create cache path E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\.pytest_cache\v\cache\nodeids: [WinError 183] Cannot create a file when that file already exists: 'E:\\IITM BS Diploma\\BSc LEVEL\\SE\\Merging Try 2\\backend\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

.venv\Lib\site-packages\_pytest\cacheprovider.py:429
  E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\.venv\Lib\site-packages\_pytest\cacheprovider.py:429: PytestCacheWarning: could not create cache path E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\.pytest_cache\v\cache\lastfailed: [WinError 183] Cannot create a file when that file already exists: 'E:\\IITM BS Diploma\\BSc LEVEL\\SE\\Merging Try 2\\backend\\.pytest_cache\\v\\cache'
    config.cache.set("cache/lastfailed", self.lastfailed)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report - assert 0 >= 1
================== 1 failed, 38 passed, 3 warnings in 9.46s ===================
```
