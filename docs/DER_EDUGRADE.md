# DER — EduGrade

Diagrama gerado a partir dos modelos SQLAlchemy.

```mermaid
erDiagram
    academic_periods {
        uuid id PK
        string name
        string code UK
        date start_date
        date end_date
        date enrollment_start
        date enrollment_end
        string status
        boolean is_current
        datetime created_at
        datetime updated_at
    }
    academic_rules {
        uuid id PK
        string name UK
        text description
        string rule_type
        text config
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    access_requests {
        uuid id PK
        string full_name
        string email
        string username
        string phone
        string requested_role
        text justification
        string status
        uuid account_id FK
        datetime created_at
        datetime updated_at
    }
    admin_settings {
        string key PK
        int value
        uuid updated_by FK
        datetime updated_at
    }
    administrators {
        uuid id PK
        uuid user_id FK
        string employee_id UK
        string department
        string permissions
        datetime created_at
        datetime updated_at
    }
    ai_corrections {
        uuid id PK
        uuid submission_id FK
        uuid question_id FK
        uuid extracted_answer_id FK
        string provider
        string model
        string status
        text recognized_text
        text interpretation
        decimal suggested_score
        decimal max_score
        text justification
        json criteria_met
        json criteria_not_met
        json conceptual_errors
        decimal ocr_confidence
        decimal evaluation_confidence
        boolean requires_review
        text review_reason
        json raw_response
        text prompt_used
        int processing_time_ms
        text error_message
        datetime created_at
        datetime completed_at
    }
    ai_provider_configs {
        uuid id PK
        string provider_id UK
        string provider_type
        string name
        string base_url
        text encrypted_api_key
        string model
        string vision_model
        json alternative_models
        json available_models
        int timeout_seconds
        int max_retries
        int priority
        boolean is_enabled
        boolean is_default
        string status
        datetime last_checked_at
        string last_error
        uuid created_by FK
        uuid updated_by FK
        datetime created_at
        datetime updated_at
    }
    answer_keys {
        uuid id PK
        uuid question_id FK
        text correct_answer
        text expected_answer
        json accepted_alternatives
        json keywords
        json required_concepts
        text justification
        json partial_scoring
        datetime created_at
        datetime updated_at
    }
    assessments {
        uuid id PK
        string title
        text description
        string type
        decimal weight
        decimal max_score
        uuid class_id FK
        uuid subject_id FK
        uuid academic_period_id FK
        date scheduled_date
        boolean is_published
        uuid created_by FK
        datetime created_at
        datetime updated_at
    }
    attendance {
        uuid id PK
        uuid enrollment_id FK
        date class_date
        boolean is_present
        boolean justified
        text justification
        uuid recorded_by FK
        datetime created_at
        datetime updated_at
    }
    audit_logs {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        text description
        json old_values
        json new_values
        string ip_address
        string user_agent
        string request_id
        string session_id
        boolean success
        text error_message
        datetime created_at
    }
    classes {
        uuid id PK
        string code UK
        string name
        uuid course_id FK
        uuid subject_id FK
        uuid academic_period_id FK
        uuid teacher_id FK
        int semester
        int year
        string schedule
        string classroom
        int max_students
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    correction_audit_logs {
        uuid id PK
        uuid review_id FK
        string action
        string field_changed
        text old_value
        text new_value
        uuid changed_by FK
        datetime changed_at
        string ip_address
        string user_agent
    }
    correction_reviews {
        uuid id PK
        uuid ai_correction_id FK
        uuid reviewed_by FK
        string status
        decimal original_suggested_score
        decimal final_score
        text corrected_text
        text reviewer_justification
        text reviewer_notes
        json criteria_overrides
        datetime started_at
        datetime completed_at
        datetime created_at
    }
    courses {
        uuid id PK
        string code UK
        string name
        text description
        int duration_semesters
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    enrollments {
        uuid id PK
        uuid student_id FK
        uuid class_id FK
        uuid academic_period_id FK
        string status
        datetime enrolled_at
        decimal final_grade
        decimal attendance_percentage
        string situation
        datetime created_at
        datetime updated_at
    }
    exam_copies {
        uuid id PK
        uuid version_id FK
        string copy_identifier UK
        text qr_code_data
        uuid student_id FK
        boolean is_personalized
        string pdf_path
        datetime printed_at
        uuid printed_by FK
        datetime created_at
    }
    exam_page_groups {
        uuid id PK
        uuid batch_id FK
        uuid student_id FK
        uuid exam_id FK
        uuid version_id FK
        string copy_identifier
        json page_ids
        string status
        decimal confidence
        json conflict_details
        uuid created_submission_id FK
        datetime created_at
    }
    exam_print_logs {
        uuid id PK
        uuid exam_id FK
        uuid version_id FK
        uuid printed_by FK
        int copy_count
        json copy_identifiers
        int status
        string pdf_path
        text error_message
        datetime started_at
        datetime completed_at
    }
    exam_questions {
        uuid id PK
        uuid exam_id FK
        int question_order
        string type
        text statement
        decimal score
        json config
        datetime created_at
        datetime updated_at
    }
    exam_submission_pages {
        uuid id PK
        uuid batch_file_id FK
        uuid submission_id FK
        int page_number
        string original_image_path
        string processed_image_path
        decimal rotation_angle
        boolean perspective_corrected
        decimal ocr_confidence
        text full_text
        json ocr_data
        datetime created_at
    }
    exam_submissions {
        uuid id PK
        uuid copy_id FK
        uuid batch_id FK
        uuid version_id FK
        uuid student_id FK
        string status
        json original_files
        json processed_files
        uuid identified_student_id FK
        decimal identification_confidence
        boolean manual_identification
        datetime submitted_at
        datetime processed_at
        datetime created_at
        datetime updated_at
    }
    exam_versions {
        uuid id PK
        uuid exam_id FK
        int version_number
        string title
        text description
        text instructions
        decimal total_score
        json questions_snapshot
        json answer_key_snapshot
        json rubrics_snapshot
        uuid published_by FK
        datetime published_at
        boolean is_active
    }
    exams {
        uuid id PK
        string title
        text description
        text instructions
        uuid class_id FK
        uuid subject_id FK
        uuid academic_period_id FK
        uuid created_by FK
        decimal total_score
        date scheduled_date
        int duration_minutes
        string status
        int version
        boolean is_template
        json print_config
        datetime created_at
        datetime updated_at
        datetime published_at
    }
    extracted_answers {
        uuid id PK
        uuid page_id FK
        uuid question_id FK
        int question_order
        text extracted_text
        string extracted_image_path
        decimal ocr_confidence
        json bounding_box
        datetime created_at
    }
    grades {
        uuid id PK
        uuid enrollment_id FK
        uuid assessment_id FK
        decimal score
        boolean is_official
        uuid graded_by FK
        datetime graded_at
        datetime published_at
        text notes
        datetime created_at
        datetime updated_at
    }
    grading_audit_logs {
        uuid id PK
        uuid batch_id FK
        uuid submission_id FK
        string action
        string entity_type
        uuid entity_id
        text description
        json old_values
        json new_values
        uuid performed_by FK
        string ai_provider
        string ai_model
        string ip_address
        string user_agent
        boolean success
        text error_message
        datetime created_at
    }
    grading_batch_files {
        uuid id PK
        uuid batch_id FK
        string original_filename
        string stored_path
        string content_type
        int file_size
        string file_type
        int page_count
        string status
        int processed_pages
        text error_message
        json ocr_data
        datetime created_at
        datetime processed_at
    }
    grading_batches {
        uuid id PK
        uuid exam_id FK
        uuid version_id FK
        uuid uploaded_by FK
        string status
        int total_files
        int processed_files
        int total_pages
        int identified_students
        int grouped_submissions
        int graded_submissions
        int pending_review
        int failed_files
        text error_message
        datetime processing_started_at
        datetime processing_completed_at
        datetime created_at
        datetime updated_at
    }
    grading_rubrics {
        uuid id PK
        uuid question_id FK
        json criteria
        decimal max_score
        datetime created_at
        datetime updated_at
    }
    student_identification_results {
        uuid id PK
        uuid page_id FK
        uuid submission_id FK
        string identified_ra
        string identified_matricula
        string identified_name
        string identified_exam_code
        string identified_class_code
        string identified_copy_code
        uuid matched_student_id FK
        decimal ra_confidence
        decimal matricula_confidence
        string match_type
        string status
        json conflict_details
        boolean manual_override
        uuid overridden_by FK
        datetime overridden_at
        string ai_provider
        string ai_model
        json raw_response
        datetime created_at
    }
    students {
        uuid id PK
        uuid user_id FK
        string ra UK
        uuid course_id
        uuid class_id
        datetime enrollment_date
        string status
        datetime created_at
        datetime updated_at
    }
    study_materials {
        uuid id PK
        uuid subject_id FK
        uuid uploaded_by FK
        string title
        text description
        string original_filename
        string stored_filename UK
        string media_type
        int file_size
        datetime created_at
    }
    subjects {
        uuid id PK
        string code UK
        string name
        text description
        int workload_hours
        int credits
        uuid course_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    submission_pages {
        uuid id PK
        uuid submission_id FK
        int page_number
        string original_image_path
        string processed_image_path
        decimal rotation_angle
        boolean perspective_corrected
        decimal ocr_confidence
        datetime created_at
    }
    system_logs {
        uuid id PK
        string level
        string logger
        text message
        string module
        string function
        int line_number
        text traceback
        json context
        uuid user_id FK
        string request_id
        datetime created_at
    }
    teacher_subjects {
        uuid id PK
        uuid teacher_id FK
        uuid subject_id FK
        uuid academic_period_id FK
        boolean is_coordinator
        datetime assigned_at
        datetime created_at
    }
    teachers {
        uuid id PK
        uuid user_id FK
        string employee_id UK
        string department
        datetime hire_date
        string status
        datetime created_at
        datetime updated_at
    }
    users {
        uuid id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        boolean is_superuser
        datetime last_login
        datetime created_at
        datetime updated_at
    }
    courses ||--o{ subjects : "course_id"
    courses ||--o{ classes : "course_id"
    subjects ||--o{ classes : "subject_id"
    academic_periods ||--o{ classes : "academic_period_id"
    teachers o|--o{ classes : "teacher_id"
    students ||--o{ enrollments : "student_id"
    classes ||--o{ enrollments : "class_id"
    academic_periods ||--o{ enrollments : "academic_period_id"
    teachers ||--o{ teacher_subjects : "teacher_id"
    subjects ||--o{ teacher_subjects : "subject_id"
    academic_periods o|--o{ teacher_subjects : "academic_period_id"
    classes ||--o{ assessments : "class_id"
    subjects ||--o{ assessments : "subject_id"
    academic_periods ||--o{ assessments : "academic_period_id"
    users ||--o{ assessments : "created_by"
    enrollments ||--o{ grades : "enrollment_id"
    assessments ||--o{ grades : "assessment_id"
    users o|--o{ grades : "graded_by"
    enrollments ||--o{ attendance : "enrollment_id"
    users ||--o{ attendance : "recorded_by"
    users o|--o{ access_requests : "account_id"
    users ||--o{ ai_provider_configs : "created_by"
    users ||--o{ ai_provider_configs : "updated_by"
    users o|--o{ admin_settings : "updated_by"
    exam_submissions ||--o{ ai_corrections : "submission_id"
    exam_questions ||--o{ ai_corrections : "question_id"
    extracted_answers o|--o{ ai_corrections : "extracted_answer_id"
    ai_corrections ||--o| correction_reviews : "ai_correction_id"
    users ||--o{ correction_reviews : "reviewed_by"
    correction_reviews ||--o{ correction_audit_logs : "review_id"
    users ||--o{ correction_audit_logs : "changed_by"
    users o|--o{ audit_logs : "user_id"
    users o|--o{ system_logs : "user_id"
    classes ||--o{ exams : "class_id"
    subjects ||--o{ exams : "subject_id"
    academic_periods ||--o{ exams : "academic_period_id"
    users ||--o{ exams : "created_by"
    exams ||--o{ exam_versions : "exam_id"
    users ||--o{ exam_versions : "published_by"
    exams ||--o{ exam_questions : "exam_id"
    exam_questions ||--o| answer_keys : "question_id"
    exam_questions ||--o| grading_rubrics : "question_id"
    exam_versions ||--o{ exam_copies : "version_id"
    students o|--o{ exam_copies : "student_id"
    users o|--o{ exam_copies : "printed_by"
    exams ||--o{ exam_print_logs : "exam_id"
    exam_versions ||--o{ exam_print_logs : "version_id"
    users ||--o{ exam_print_logs : "printed_by"
    exam_copies o|--o{ exam_submissions : "copy_id"
    grading_batches o|--o{ exam_submissions : "batch_id"
    exam_versions ||--o{ exam_submissions : "version_id"
    students o|--o{ exam_submissions : "student_id"
    students o|--o{ exam_submissions : "identified_student_id"
    exam_submissions ||--o{ submission_pages : "submission_id"
    submission_pages ||--o{ extracted_answers : "page_id"
    exam_questions ||--o{ extracted_answers : "question_id"
    exams ||--o{ grading_batches : "exam_id"
    exam_versions ||--o{ grading_batches : "version_id"
    users ||--o{ grading_batches : "uploaded_by"
    grading_batches ||--o{ grading_batch_files : "batch_id"
    grading_batch_files ||--o{ exam_submission_pages : "batch_file_id"
    exam_submissions o|--o{ exam_submission_pages : "submission_id"
    exam_submission_pages ||--o{ student_identification_results : "page_id"
    exam_submissions o|--o{ student_identification_results : "submission_id"
    students o|--o{ student_identification_results : "matched_student_id"
    users o|--o{ student_identification_results : "overridden_by"
    grading_batches ||--o{ exam_page_groups : "batch_id"
    students o|--o{ exam_page_groups : "student_id"
    exams ||--o{ exam_page_groups : "exam_id"
    exam_versions ||--o{ exam_page_groups : "version_id"
    exam_submissions o|--o{ exam_page_groups : "created_submission_id"
    grading_batches ||--o{ grading_audit_logs : "batch_id"
    exam_submissions o|--o{ grading_audit_logs : "submission_id"
    users o|--o{ grading_audit_logs : "performed_by"
    subjects ||--o{ study_materials : "subject_id"
    users ||--o{ study_materials : "uploaded_by"
    users ||--o| students : "user_id"
    users ||--o| teachers : "user_id"
    users ||--o| administrators : "user_id"
```

> DER gerado automaticamente. As cardinalidades são aproximações baseadas em FK, nullable e unique. Restrições compostas e regras de negócio exigem revisão.
