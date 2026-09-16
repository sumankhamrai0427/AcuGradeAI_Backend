-- ============================================================
-- ACUGRADE AI — FULL DATABASE SCHEMA, SEED DATA & PROCEDURES
-- Charset: utf8mb4 (Supports multilingual symbols & emoji)
-- Engine: InnoDB
-- ============================================================

CREATE DATABASE IF NOT EXISTS AcuGrade_AI CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE AcuGrade_AI;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. ROLES & DYNAMIC PAGE ACCESS
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  role_name   VARCHAR(50)  NOT NULL UNIQUE, -- 'STUDENT', 'PARENT', 'TEACHER', 'ADMIN'
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_roles_name (role_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS role_page_access (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  role_id     INT          NOT NULL,
  page_name   VARCHAR(100) NOT NULL,
  page_route  VARCHAR(100) NOT NULL,
  icon        VARCHAR(50)  NULL,
  menu_order  INT          NOT NULL DEFAULT 1,
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_role_page_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
  UNIQUE KEY uq_role_page (role_id, page_route),
  KEY idx_role_page_active (role_id, is_active)
) ENGINE=InnoDB;

-- ============================================================
-- 2. USERS & AUTH
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(150) NOT NULL,
  username      VARCHAR(100) NULL,
  email         VARCHAR(190) NOT NULL,
  password_hash VARCHAR(255) NULL,
  role_id       INT          NOT NULL,
  auth_provider ENUM('EMAIL', 'GOOGLE') NOT NULL DEFAULT 'EMAIL',
  google_id     VARCHAR(100) NULL,
  is_active     TINYINT(1)   NOT NULL DEFAULT 1,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by    INT          NULL,
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by    INT          NULL,
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_google_id (google_id),
  CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
  KEY idx_users_role_id (role_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT          NOT NULL,
  token_hash  VARCHAR(255) NOT NULL,
  expires_at  DATETIME     NOT NULL,
  revoked     TINYINT(1)   NOT NULL DEFAULT 0,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  KEY idx_refresh_user (user_id),
  KEY idx_refresh_token_hash (token_hash)
) ENGINE=InnoDB;

-- ============================================================
-- 3. PARENT / STUDENT / TEACHER PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS parents (
  id                  INT NOT NULL PRIMARY KEY, -- == users.id
  subscription_tier   ENUM('free','scholar_pro','genius_competitive') NOT NULL DEFAULT 'free',
  subscription_expiry DATETIME NULL,
  CONSTRAINT fk_parents_user FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS teachers (
  id          INT          NOT NULL PRIMARY KEY, -- == users.id
  role_title  VARCHAR(120) NOT NULL DEFAULT 'Subject Teacher',
  subject     VARCHAR(60)  NULL,
  school_name VARCHAR(190) NOT NULL,
  phone       VARCHAR(30)  NULL,
  verified    TINYINT(1)   NOT NULL DEFAULT 0,
  CONSTRAINT fk_teachers_user FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
  id                      INT          NOT NULL PRIMARY KEY, -- == users.id
  parent_id               INT          NOT NULL,
  teacher_id              INT          NULL,
  avatar                  VARCHAR(20)  NOT NULL DEFAULT '🧑‍🎓',
  class_grade             VARCHAR(20)  NOT NULL,
  target_board            VARCHAR(20)  NOT NULL,
  school_name             VARCHAR(190) NULL,
  school_email            VARCHAR(190) NULL,
  pin_hash                VARCHAR(255) NOT NULL,
  daily_exams_taken_today INT          NOT NULL DEFAULT 0,
  last_exam_date          DATE         NULL,
  total_exams_taken       INT          NOT NULL DEFAULT 0,
  average_score           DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  streak_days             INT          NOT NULL DEFAULT 0,
  xp                      INT          NOT NULL DEFAULT 250,
  level                   INT          NOT NULL DEFAULT 1,
  created_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_students_user    FOREIGN KEY (id)         REFERENCES users(id)    ON DELETE CASCADE,
  CONSTRAINT fk_students_parent  FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
  CONSTRAINT fk_students_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
  KEY idx_students_parent (parent_id),
  KEY idx_students_teacher (teacher_id)
) ENGINE=InnoDB;

-- ============================================================
-- 4. CURRICULUM & QUESTION BANK MASTERS
-- ============================================================
CREATE TABLE IF NOT EXISTS board_master (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  board_name  VARCHAR(100) NOT NULL,
  description TEXT NULL,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS class_master (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  class_name  VARCHAR(100) NOT NULL,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subject_master (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  board_id     INT NOT NULL,
  class_id     INT NOT NULL,
  subject_name VARCHAR(100) NOT NULL,
  is_active    TINYINT(1) DEFAULT 1,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_subject_board FOREIGN KEY (board_id) REFERENCES board_master (id) ON DELETE CASCADE,
  CONSTRAINT fk_subject_class FOREIGN KEY (class_id) REFERENCES class_master (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chapter_master (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  subject_id   INT NOT NULL,
  chapter_name VARCHAR(255) NOT NULL,
  is_active    TINYINT(1) DEFAULT 1,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_chapter_subject FOREIGN KEY (subject_id) REFERENCES subject_master (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS topic_master (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  chapter_id  INT NOT NULL,
  topic_name  VARCHAR(255) NOT NULL,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_topic_chapter FOREIGN KEY (chapter_id) REFERENCES chapter_master (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS difficulty_level_master (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  difficulty_level_name VARCHAR(100) NOT NULL,
  is_active             TINYINT(1) DEFAULT 1,
  created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS question_type_master (
  id                 INT AUTO_INCREMENT PRIMARY KEY,
  question_type_name VARCHAR(100) NOT NULL,
  default_marks      INT NOT NULL DEFAULT 1,
  is_active          TINYINT(1) DEFAULT 1,
  created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS question_master (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  topic_id            INT NOT NULL,
  question_type_id    INT NOT NULL,
  difficulty_level_id INT NOT NULL,
  question            TEXT NOT NULL,
  options             JSON DEFAULT NULL,
  correct_answer      VARCHAR(500) NOT NULL,
  explanation         TEXT NULL,
  marks               INT NOT NULL DEFAULT 1,
  is_active           TINYINT(1) DEFAULT 1,
  created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_question_topic FOREIGN KEY (topic_id) REFERENCES topic_master (id) ON DELETE CASCADE,
  CONSTRAINT fk_question_type FOREIGN KEY (question_type_id) REFERENCES question_type_master (id) ON DELETE RESTRICT,
  CONSTRAINT fk_question_difficulty FOREIGN KEY (difficulty_level_id) REFERENCES difficulty_level_master (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS question_upload_batches (
  id                      INT AUTO_INCREMENT PRIMARY KEY,
  file_name               VARCHAR(255) NOT NULL,
  file_size_bytes         INT DEFAULT 0,
  total_rows              INT DEFAULT 0,
  inserted_count          INT DEFAULT 0,
  updated_count           INT DEFAULT 0,
  duplicate_skipped_count INT DEFAULT 0,
  status                  VARCHAR(50) DEFAULT 'SUCCESS',
  uploaded_by             INT NULL,
  created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_qub_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 5. RUNBOOKS & RAG DOCUMENT STORE
-- ============================================================
CREATE TABLE IF NOT EXISTS runbooks (
  id                         CHAR(36)     NOT NULL PRIMARY KEY,
  board                      VARCHAR(20)  NOT NULL,
  class_grade                VARCHAR(20)  NOT NULL,
  subject                    VARCHAR(40)  NOT NULL,
  chapter_name               VARCHAR(190) NOT NULL,
  core_concepts              JSON NOT NULL,
  key_formulas_or_rules      JSON NOT NULL,
  common_traps               JSON NOT NULL,
  curated_reference_urls     JSON NOT NULL,
  sample_question_archetypes JSON NOT NULL,
  difficulty_calibration     JSON NOT NULL,
  status                     ENUM('DRAFT','PUBLISHED','ARCHIVED') NOT NULL DEFAULT 'PUBLISHED',
  version                    INT NOT NULL DEFAULT 1,
  created_by                 INT NULL,
  created_at                 DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at                 DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_runbooks_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  KEY idx_runbooks_filter (board, class_grade, subject),
  KEY idx_runbooks_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS documents (
  id           CHAR(36)     NOT NULL PRIMARY KEY,
  runbook_id   CHAR(36)     NULL,
  filename     VARCHAR(255) NOT NULL,
  content_type VARCHAR(100) NOT NULL,
  board        VARCHAR(20)  NULL,
  class_grade  VARCHAR(20)  NULL,
  subject      VARCHAR(40)  NULL,
  uploaded_by  INT          NULL,
  status       ENUM('PENDING','PROCESSED','FAILED') NOT NULL DEFAULT 'PENDING',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_documents_runbook FOREIGN KEY (runbook_id) REFERENCES runbooks(id) ON DELETE SET NULL,
  CONSTRAINT fk_documents_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS document_chunks (
  id           CHAR(36)     NOT NULL PRIMARY KEY,
  document_id  CHAR(36)     NOT NULL,
  chunk_index  INT          NOT NULL,
  content      TEXT         NOT NULL,
  vector_id    VARCHAR(100) NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_chunks_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
  KEY idx_chunks_document (document_id)
) ENGINE=InnoDB;

-- ============================================================
-- 6. EXAMS / QUESTIONS / SUBMISSIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS exams (
  id                       CHAR(36)     NOT NULL PRIMARY KEY,
  student_id               INT          NOT NULL,
  title                    VARCHAR(255) NOT NULL,
  board                    VARCHAR(20)  NOT NULL,
  class_grade              VARCHAR(20)  NOT NULL,
  subject                  VARCHAR(40)  NOT NULL,
  difficulty               ENUM('simple','medium','hard') NOT NULL,
  total_marks              INT NOT NULL DEFAULT 10,
  question_count           INT NOT NULL DEFAULT 10,
  time_limit_minutes       INT NOT NULL DEFAULT 15,
  rag_knowledge_nodes_used JSON NULL,
  source                   ENUM('mistral-rag','rag-engine-curated') NOT NULL,
  status                   ENUM('GENERATED','IN_PROGRESS','SUBMITTED','EXPIRED') NOT NULL DEFAULT 'GENERATED',
  created_at               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_exams_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  KEY idx_exams_student (student_id),
  KEY idx_exams_created (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS questions (
  id               CHAR(36)     NOT NULL PRIMARY KEY,
  exam_id          CHAR(36)     NOT NULL,
  question_number  INT NOT NULL,
  type             ENUM('mcq','objective','numerical','logical','saq') NOT NULL,
  question_text    TEXT NOT NULL,
  options          JSON NULL,
  correct_answer   VARCHAR(500) NOT NULL,
  explanation      TEXT NOT NULL,
  difficulty       ENUM('simple','medium','hard') NOT NULL,
  marks            INT NOT NULL DEFAULT 1,
  topic            VARCHAR(190) NOT NULL,
  reference_links  JSON NULL,
  hint             TEXT NULL,
  CONSTRAINT fk_questions_exam FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
  KEY idx_questions_exam (exam_id),
  KEY idx_questions_topic (topic)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exam_submissions (
  id                    CHAR(36)     NOT NULL PRIMARY KEY,
  exam_id               CHAR(36)     NOT NULL,
  student_id            INT          NOT NULL,
  answers               JSON NOT NULL,
  marks_obtained        DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  total_marks           INT NOT NULL DEFAULT 10,
  accuracy_percentage   DECIMAL(5,2) NOT NULL,
  time_taken_seconds    INT NOT NULL,
  submitted_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_submissions_exam FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
  CONSTRAINT fk_submissions_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  UNIQUE KEY uq_submission_per_exam (exam_id),
  KEY idx_submissions_student (student_id),
  KEY idx_submissions_submitted (submitted_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS question_evaluations (
  id                       CHAR(36)     NOT NULL PRIMARY KEY,
  submission_id            CHAR(36)     NOT NULL,
  question_id              CHAR(36)     NOT NULL,
  student_answer           VARCHAR(500) NOT NULL,
  is_correct               TINYINT(1)   NOT NULL,
  marks_awarded            DECIMAL(4,2) NOT NULL DEFAULT 0.00,
  misconception_identified VARCHAR(255) NULL,
  feedback                 TEXT         NULL,
  CONSTRAINT fk_qe_submission FOREIGN KEY (submission_id) REFERENCES exam_submissions(id) ON DELETE CASCADE,
  CONSTRAINT fk_qe_question   FOREIGN KEY (question_id)   REFERENCES questions(id) ON DELETE CASCADE,
  KEY idx_qe_submission (submission_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS diagnostic_analyses (
  id                        CHAR(36)     NOT NULL PRIMARY KEY,
  submission_id             CHAR(36)     NOT NULL,
  overall_band              ENUM('Needs Foundation','Developing','Proficient','Advanced Mastery','Competitive Ready') NOT NULL,
  mastery_score_percentage  DECIMAL(5,2) NOT NULL,
  strengths                 JSON NOT NULL,
  areas_to_improve          JSON NOT NULL,
  k_graph_insights          JSON NOT NULL,
  evolutionary_roadmap      TEXT NOT NULL,
  encouragement_note        TEXT NOT NULL,
  recommended_next_exam     JSON NOT NULL,
  curated_study_links       JSON NOT NULL,
  source                    ENUM('mistral','fallback') NOT NULL,
  created_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_diag_submission FOREIGN KEY (submission_id) REFERENCES exam_submissions(id) ON DELETE CASCADE,
  UNIQUE KEY uq_diag_per_submission (submission_id)
) ENGINE=InnoDB;

-- ============================================================
-- 7. MASTERY / MISCONCEPTIONS / LEARNING PATH
-- ============================================================
CREATE TABLE IF NOT EXISTS mastery (
  id               CHAR(36)     NOT NULL PRIMARY KEY,
  student_id       INT          NOT NULL,
  topic            VARCHAR(190) NOT NULL,
  mastery_score    DECIMAL(5,2) NOT NULL DEFAULT 0,
  confidence       DECIMAL(5,2) NOT NULL DEFAULT 0,
  attempt_count    INT NOT NULL DEFAULT 0,
  correct_count    INT NOT NULL DEFAULT 0,
  status           ENUM('NOT_STARTED','LEARNING','DEVELOPING','MASTERED','CRITICAL_GAP') NOT NULL DEFAULT 'NOT_STARTED',
  last_assessed_at DATETIME NULL,
  CONSTRAINT fk_mastery_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  UNIQUE KEY uq_mastery_student_topic (student_id, topic),
  KEY idx_mastery_student (student_id),
  KEY idx_mastery_topic (topic)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS misconceptions (
  id           CHAR(36)     NOT NULL PRIMARY KEY,
  student_id   INT          NOT NULL,
  topic        VARCHAR(190) NOT NULL,
  description  VARCHAR(500) NOT NULL,
  evidence     TEXT NULL,
  severity     ENUM('LOW','MEDIUM','HIGH') NOT NULL DEFAULT 'MEDIUM',
  status       ENUM('OPEN','IMPROVING','RESOLVED') NOT NULL DEFAULT 'OPEN',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_misconceptions_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  KEY idx_misconceptions_student (student_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS learning_path_nodes (
  id                    CHAR(36)     NOT NULL PRIMARY KEY,
  student_id            INT          NOT NULL,
  topic                 VARCHAR(190) NOT NULL,
  chapter_name          VARCHAR(190) NOT NULL,
  subject               VARCHAR(40)  NOT NULL,
  class_grade           VARCHAR(20)  NOT NULL,
  board                 VARCHAR(20)  NOT NULL,
  status                ENUM('locked','available','in_progress','mastered','remedial_needed') NOT NULL DEFAULT 'available',
  mastery_percentage    DECIMAL(5,2) NOT NULL DEFAULT 0,
  level                 ENUM('foundational','intermediate','advanced_hots') NOT NULL DEFAULT 'foundational',
  prerequisites         JSON NULL,
  key_concepts          JSON NULL,
  common_misconceptions JSON NULL,
  curated_resources     JSON NULL,
  practice_exam_config  JSON NULL,
  recommended_reason    VARCHAR(500) NULL,
  attempts_count        INT NOT NULL DEFAULT 0,
  last_score            INT NULL,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_lp_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  KEY idx_lp_student (student_id)
) ENGINE=InnoDB;

-- ============================================================
-- 8. GAMIFICATION & REWARDS
-- ============================================================
CREATE TABLE IF NOT EXISTS badges (
  id               VARCHAR(60)  NOT NULL PRIMARY KEY,
  title            VARCHAR(150) NOT NULL,
  description      VARCHAR(255) NOT NULL,
  icon             VARCHAR(20)  NOT NULL DEFAULT '🏆',
  tier             ENUM('bronze','silver','gold','diamond') NOT NULL DEFAULT 'bronze',
  category         ENUM('mastery','streak','score','speed','explorer') NOT NULL DEFAULT 'mastery',
  xp_reward        INT NOT NULL DEFAULT 0,
  requirement_text VARCHAR(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS student_badges (
  student_id  INT         NOT NULL,
  badge_id    VARCHAR(60) NOT NULL,
  unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (student_id, badge_id),
  CONSTRAINT fk_sb_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_sb_badge FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS xp_events (
  id          CHAR(36)     NOT NULL PRIMARY KEY,
  student_id  INT          NOT NULL,
  amount      INT NOT NULL,
  reason      VARCHAR(190) NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_xp_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  KEY idx_xp_student (student_id)
) ENGINE=InnoDB;

-- ============================================================
-- 9. PARENT-TEACHER COMMUNICATION & REPORTS
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
  id          CHAR(36) NOT NULL PRIMARY KEY,
  parent_id   INT NOT NULL,
  teacher_id  INT NOT NULL,
  student_id  INT NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_conv_parent  FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
  CONSTRAINT fk_conv_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
  CONSTRAINT fk_conv_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  UNIQUE KEY uq_conv (parent_id, teacher_id, student_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS messages (
  id                          CHAR(36)     NOT NULL PRIMARY KEY,
  conversation_id             CHAR(36)     NOT NULL,
  sender_role                 ENUM('parent','teacher') NOT NULL,
  sender_id                   INT          NOT NULL,
  message                     TEXT NOT NULL,
  attached_submission_id      CHAR(36) NULL,
  action_items                JSON NULL,
  status                      ENUM('sent','delivered','read','action_taken') NOT NULL DEFAULT 'sent',
  created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_msg_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  CONSTRAINT fk_msg_submission FOREIGN KEY (attached_submission_id) REFERENCES exam_submissions(id) ON DELETE SET NULL,
  KEY idx_messages_conversation (conversation_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS shared_dossiers (
  id                          CHAR(36)     NOT NULL PRIMARY KEY,
  student_id                  INT          NOT NULL,
  parent_id                   INT          NOT NULL,
  share_token                 VARCHAR(60)  NOT NULL,
  notes                       TEXT NULL,
  recipients                  JSON NOT NULL,
  included_submissions_count  INT NOT NULL DEFAULT 0,
  status                      ENUM('active','revoked') NOT NULL DEFAULT 'active',
  created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at                  DATETIME NOT NULL,
  CONSTRAINT fk_dossier_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_dossier_parent  FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
  UNIQUE KEY uq_dossier_token (share_token)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ptm_schedules (
  id           CHAR(36)     NOT NULL PRIMARY KEY,
  parent_id    INT          NOT NULL,
  teacher_id   INT          NOT NULL,
  student_id   INT          NOT NULL,
  scheduled_at DATETIME     NOT NULL,
  topic        VARCHAR(255) NOT NULL,
  meeting_link VARCHAR(255) NULL,
  status       ENUM('SCHEDULED','COMPLETED','CANCELLED') NOT NULL DEFAULT 'SCHEDULED',
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ptm_parent  FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
  CONSTRAINT fk_ptm_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
  CONSTRAINT fk_ptm_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 10. SUBSCRIPTIONS & PLANS
-- ============================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
  id                 VARCHAR(30) NOT NULL PRIMARY KEY,
  name               VARCHAR(150) NOT NULL,
  price_monthly      DECIMAL(8,2) NOT NULL,
  price_yearly       DECIMAL(8,2) NOT NULL,
  currency           VARCHAR(10) NOT NULL DEFAULT 'USD',
  badge              VARCHAR(100) NULL,
  description        VARCHAR(500) NOT NULL,
  features           JSON NOT NULL,
  daily_exam_limit   VARCHAR(20) NOT NULL,
  max_children       VARCHAR(20) NOT NULL,
  is_popular         TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subscriptions (
  id            CHAR(36)    NOT NULL PRIMARY KEY,
  parent_id     INT         NOT NULL,
  plan_id       VARCHAR(30) NOT NULL,
  status        ENUM('ACTIVE','EXPIRED','CANCELLED') NOT NULL DEFAULT 'ACTIVE',
  start_date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  end_date      DATETIME NULL,
  CONSTRAINT fk_sub_parent FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE,
  CONSTRAINT fk_sub_plan   FOREIGN KEY (plan_id)   REFERENCES subscription_plans(id),
  KEY idx_sub_parent (parent_id)
) ENGINE=InnoDB;

-- ============================================================
-- 11. AUDIT LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
  id          CHAR(36)     NOT NULL PRIMARY KEY,
  user_id     INT          NULL,
  action      VARCHAR(120) NOT NULL,
  entity_type VARCHAR(60)  NULL,
  entity_id   VARCHAR(60)  NULL,
  ip_address  VARCHAR(64)  NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  KEY idx_audit_user (user_id),
  KEY idx_audit_created (created_at)
) ENGINE=InnoDB;

-- ============================================================
-- 12. BLOGS & CONTENT
-- ============================================================
CREATE TABLE IF NOT EXISTS author_master (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS category_master (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS blogs (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  title            VARCHAR(255) NOT NULL,
  author_id        INT NOT NULL,
  category_id      INT NOT NULL,
  introduction     TEXT NULL,
  content          TEXT NULL,
  image_url        VARCHAR(500) NULL,
  is_pinned        TINYINT(1) NOT NULL DEFAULT 0,
  tags             JSON NULL,
  meta_title       VARCHAR(255) NULL,
  meta_description TEXT NULL,
  meta_keywords    TEXT NULL,
  canonical_url    VARCHAR(500) NULL,
  status           ENUM('Published','Draft') NOT NULL DEFAULT 'Draft',
  shares_count     INT NOT NULL DEFAULT 0,
  date             DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_blog_author FOREIGN KEY (author_id) REFERENCES author_master(id),
  CONSTRAINT fk_blog_category FOREIGN KEY (category_id) REFERENCES category_master(id)
) ENGINE=InnoDB;


-- ============================================================
-- 13. MASTER SEED DATA (SAFE INSERT-IF-NOT-EXISTS)
-- ============================================================

-- Roles
INSERT INTO roles (id, role_name, is_active) VALUES
(1, 'STUDENT', 1),
(2, 'PARENT', 1),
(3, 'TEACHER', 1),
(4, 'ADMIN', 1)
ON DUPLICATE KEY UPDATE is_active = 1;

-- Boards
INSERT INTO board_master (id, board_name, description, is_active) VALUES
(1, 'CBSE', 'Central Board of Secondary Education', 1),
(2, 'ICSE', 'Indian Certificate of Secondary Education (Class 1-10)', 1),
(3, 'WBBSE', 'West Bengal Board of Secondary Education (Class 1-10)', 1),
(4, 'WBCHSE', 'West Bengal Council of Higher Secondary Education (Class 11-12)', 1),
(5, 'ISC', 'Indian School Certificate (Class 11-12)', 1),
(6, 'UK-Cambridge', 'Cambridge Assessment International Education (CAIE / IGCSE)', 1),
(7, 'NCERT', 'National Council of Educational Research and Training', 1),
(8, 'NEET', 'National Eligibility cum Entrance Test (Medical UG Foundation)', 1),
(9, 'IIT', 'Joint Entrance Examination (JEE Main & Advanced Foundation)', 1)
ON DUPLICATE KEY UPDATE board_name = VALUES(board_name), description = VALUES(description), is_active = 1;

-- Classes
INSERT INTO class_master (id, class_name, is_active) VALUES
(1, 'Class 1', 1),
(2, 'Class 2', 1),
(3, 'Class 3', 1),
(4, 'Class 4', 1),
(5, 'Class 5', 1),
(6, 'Class 6', 1),
(7, 'Class 7', 1),
(8, 'Class 8', 1),
(9, 'Class 9', 1),
(10, 'Class 10', 1),
(11, 'Class 11', 1),
(12, 'Class 12', 1)
ON DUPLICATE KEY UPDATE class_name = VALUES(class_name), is_active = 1;

-- Question Types
INSERT INTO question_type_master (id, question_type_name, default_marks, is_active) VALUES
(1, 'MCQ', 1, 1),
(2, 'Objective', 1, 1),
(3, 'SAQ', 2, 1),
(4, 'Numerical', 2, 1),
(5, 'Logical', 2, 1)
ON DUPLICATE KEY UPDATE question_type_name = VALUES(question_type_name), default_marks = VALUES(default_marks), is_active = 1;

-- Difficulty Levels
INSERT INTO difficulty_level_master (id, difficulty_level_name, is_active) VALUES
(1, 'simple', 1),
(2, 'medium', 1),
(3, 'hard', 1)
ON DUPLICATE KEY UPDATE difficulty_level_name = VALUES(difficulty_level_name), is_active = 1;

-- Gamification Badges
INSERT INTO badges (id, title, description, icon, tier, category, xp_reward, requirement_text) VALUES
('badge-pioneer', 'Pioneer', 'Took your first diagnostic exam', '🌟', 'bronze', 'explorer', 50, 'Complete 1 diagnostic exam'),
('badge-perfect-10', 'Perfect 10', 'Scored a flawless 10/10', '🎯', 'gold', 'score', 100, 'Score 100% on any exam'),
('badge-speed-demon', 'Speed Demon', 'Scored 8+ in under 6 minutes', '⚡', 'silver', 'speed', 75, 'Finish exam with 80%+ under 6 min'),
('badge-streak-7', '7-Day Streak', 'Maintained a 7-day streak', '🔥', 'diamond', 'streak', 150, 'Practice 7 days in a row')
ON DUPLICATE KEY UPDATE title = VALUES(title), description = VALUES(description);

-- Subscription Plans
INSERT INTO subscription_plans (id, name, price_monthly, price_yearly, currency, badge, description, features, daily_exam_limit, max_children, is_popular) VALUES
('free', 'Explorer Free', 0.00, 0.00, 'INR', 'Free', 'Standard foundational diagnostic tests for single child', '["1 Child Account", "1 Diagnostic Exam / day", "Standard Answer Explanations", "Community Support"]', '1', '1', 0),
('scholar_pro', 'Scholar Pro', 499.00, 4999.00, 'INR', 'Popular', 'Full adaptive diagnostic engine for up to 3 children', '["Up to 3 Children Accounts", "Unlimited Diagnostic Exams", "Deep Mistral AI Error Diagnostics", "Dynamic Learning Path & Roadmaps", "Teacher Dossier Sharing & PTM Scheduler"]', 'unlimited', '3', 1),
('genius_competitive', 'Genius Competitive', 999.00, 8999.00, 'INR', 'Ultimate', 'Comprehensive board + competitive (NEET/JEE) preparation for up to 5 children', '["Up to 5 Children Accounts", "Unlimited Diagnostic & Mock Exams", "NEET / JEE Foundation Trackers", "Deep Misconception Root-Cause Mapping", "Priority AI Teacher-Parent Co-Pilot"]', 'unlimited', '5', 0)
ON DUPLICATE KEY UPDATE name = VALUES(name), price_monthly = VALUES(price_monthly), price_yearly = VALUES(price_yearly);

-- ------------------------------------------------------------
-- SUBJECTS SEEDING FOR ALL BOARDS & CLASSES
-- ------------------------------------------------------------

-- A. Primary Classes (Class 1 to 5) for CBSE, ICSE, WBBSE, UK-Cambridge, NCERT
INSERT INTO subject_master (board_id, class_id, subject_name, is_active)
SELECT b.id, c.id, s.name, 1
FROM board_master b
CROSS JOIN class_master c
CROSS JOIN (
    SELECT 'Mathematics' AS name UNION SELECT 'English' UNION SELECT 'Science' 
    UNION SELECT 'Social Studies' UNION SELECT 'Computer Science' UNION SELECT 'Logical Reasoning'
) s
WHERE b.board_name IN ('CBSE', 'ICSE', 'WBBSE', 'UK-Cambridge', 'NCERT')
  AND c.class_name IN ('Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5')
  AND NOT EXISTS (
      SELECT 1 FROM subject_master sm 
      WHERE sm.board_id = b.id AND sm.class_id = c.id AND sm.subject_name = s.name
  );

-- B. Middle & Secondary Classes (Class 6 to 10) for CBSE, ICSE, WBBSE, UK-Cambridge, NCERT
INSERT INTO subject_master (board_id, class_id, subject_name, is_active)
SELECT b.id, c.id, s.name, 1
FROM board_master b
CROSS JOIN class_master c
CROSS JOIN (
    SELECT 'Mathematics' AS name UNION SELECT 'Science' UNION SELECT 'Physics' 
    UNION SELECT 'Chemistry' UNION SELECT 'Biology' UNION SELECT 'Social Studies' 
    UNION SELECT 'English' UNION SELECT 'Computer Science' UNION SELECT 'Logical Reasoning'
) s
WHERE b.board_name IN ('CBSE', 'ICSE', 'WBBSE', 'UK-Cambridge', 'NCERT')
  AND c.class_name IN ('Class 6', 'Class 7', 'Class 8', 'Class 9', 'Class 10')
  AND NOT EXISTS (
      SELECT 1 FROM subject_master sm 
      WHERE sm.board_id = b.id AND sm.class_id = c.id AND sm.subject_name = s.name
  );

-- C. Higher Secondary Classes (Class 11 & 12) for CBSE, ISC, WBCHSE, UK-Cambridge, NCERT, NEET, IIT
INSERT INTO subject_master (board_id, class_id, subject_name, is_active)
SELECT b.id, c.id, s.name, 1
FROM board_master b
CROSS JOIN class_master c
CROSS JOIN (
    SELECT 'Mathematics' AS name UNION SELECT 'Physics' UNION SELECT 'Chemistry' 
    UNION SELECT 'Biology' UNION SELECT 'Computer Science' UNION SELECT 'English' UNION SELECT 'Logical Reasoning'
) s
WHERE b.board_name IN ('CBSE', 'ISC', 'WBCHSE', 'UK-Cambridge', 'NCERT', 'NEET', 'IIT')
  AND c.class_name IN ('Class 11', 'Class 12')
  AND NOT EXISTS (
      SELECT 1 FROM subject_master sm 
      WHERE sm.board_id = b.id AND sm.class_id = c.id AND sm.subject_name = s.name
  );

-- ------------------------------------------------------------
-- DEFAULT CHAPTERS FOR ALL SUBJECTS
-- ------------------------------------------------------------
INSERT INTO chapter_master (subject_id, chapter_name, is_active)
SELECT s.id, CONCAT('General Concepts of ', s.subject_name), 1
FROM subject_master s
WHERE s.is_active = 1
  AND NOT EXISTS (
      SELECT 1 FROM chapter_master ch WHERE ch.subject_id = s.id
  );

-- ------------------------------------------------------------
-- DEFAULT TOPICS FOR ALL CHAPTERS
-- ------------------------------------------------------------
INSERT INTO topic_master (chapter_id, topic_name, is_active)
SELECT ch.id, 'Core Theory & Concepts', 1
FROM chapter_master ch
WHERE ch.is_active = 1
  AND NOT EXISTS (
      SELECT 1 FROM topic_master t WHERE t.chapter_id = ch.id
  );


-- ============================================================
-- 14. STORED PROCEDURES
-- ============================================================
DROP PROCEDURE IF EXISTS sp_register_parent;
DROP PROCEDURE IF EXISTS sp_google_login_or_register;
DROP PROCEDURE IF EXISTS sp_get_user_for_login;
DROP PROCEDURE IF EXISTS sp_verify_user_session;
DROP PROCEDURE IF EXISTS sp_get_child_for_login;
DROP PROCEDURE IF EXISTS sp_save_refresh_token;
DROP PROCEDURE IF EXISTS sp_validate_and_rotate_refresh_token;
DROP PROCEDURE IF EXISTS sp_revoke_refresh_token;
DROP PROCEDURE IF EXISTS sp_get_role_menu_permissions;
DROP PROCEDURE IF EXISTS sp_get_registration_roles;
DROP PROCEDURE IF EXISTS sp_get_child_registration_masters;
DROP PROCEDURE IF EXISTS sp_add_child_account;
DROP PROCEDURE IF EXISTS sp_generate_quick_test_from_db;
DROP PROCEDURE IF EXISTS sp_generate_exam_from_db;

DELIMITER //

CREATE PROCEDURE sp_register_parent(
    IN p_name VARCHAR(150),
    IN p_email VARCHAR(190),
    IN p_password_hash VARCHAR(255),
    IN p_role_name VARCHAR(50)
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_role_id INT;
    DECLARE v_email_count INT;

    SELECT COUNT(*) INTO v_email_count FROM users WHERE email = p_email;
    IF v_email_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'EMAIL_TAKEN';
    ELSE
        SELECT id INTO v_role_id FROM roles WHERE UPPER(role_name) = UPPER(p_role_name) LIMIT 1;
        IF v_role_id IS NULL THEN
            SELECT id INTO v_role_id FROM roles WHERE UPPER(role_name) = 'PARENT' LIMIT 1;
        END IF;

        INSERT INTO users (name, email, password_hash, role_id, auth_provider, is_active, created_at, updated_at)
        VALUES (p_name, p_email, p_password_hash, v_role_id, 'EMAIL', 1, NOW(), NOW());

        SET v_user_id = LAST_INSERT_ID();
        
        IF UPPER(p_role_name) = 'TEACHER' THEN
            INSERT INTO teachers (id, role_title, subject, school_name, verified)
            VALUES (v_user_id, 'Subject Teacher', 'General', 'Partner School', 1);
        ELSE
            INSERT INTO parents (id, subscription_tier) VALUES (v_user_id, 'free');
        END IF;

        SELECT u.id, u.name, u.email, u.role_id, r.role_name, IFNULL(p.subscription_tier, 'free') AS subscription_tier, u.is_active, u.created_at, u.auth_provider, u.google_id
        FROM users u
        JOIN roles r ON u.role_id = r.id
        LEFT JOIN parents p ON u.id = p.id
        WHERE u.id = v_user_id;
    END IF;
END //

CREATE PROCEDURE sp_google_login_or_register(
    IN p_name VARCHAR(150),
    IN p_email VARCHAR(190),
    IN p_google_id VARCHAR(100),
    IN p_role_name VARCHAR(50)
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_role_id INT;

    SELECT id INTO v_user_id FROM users WHERE email = p_email OR (p_google_id IS NOT NULL AND google_id = p_google_id) LIMIT 1;

    IF v_user_id IS NOT NULL THEN
        UPDATE users 
        SET google_id = IFNULL(google_id, p_google_id),
            updated_at = NOW()
        WHERE id = v_user_id;
    ELSE
        SELECT id INTO v_role_id FROM roles WHERE UPPER(role_name) = UPPER(p_role_name) LIMIT 1;
        IF v_role_id IS NULL THEN
            SELECT id INTO v_role_id FROM roles WHERE UPPER(role_name) = 'PARENT' LIMIT 1;
        END IF;

        INSERT INTO users (name, email, password_hash, role_id, auth_provider, google_id, is_active, created_at, updated_at)
        VALUES (p_name, p_email, NULL, v_role_id, 'GOOGLE', p_google_id, 1, NOW(), NOW());

        SET v_user_id = LAST_INSERT_ID();

        IF UPPER(p_role_name) = 'TEACHER' THEN
            INSERT INTO teachers (id, role_title, subject, school_name, verified)
            VALUES (v_user_id, 'Subject Teacher', 'General', 'Partner School', 1);
        ELSE
            INSERT INTO parents (id, subscription_tier) VALUES (v_user_id, 'free');
        END IF;
    END IF;

    SELECT u.id, u.name, u.email, u.role_id, r.role_name, IFNULL(p.subscription_tier, 'free') AS subscription_tier, u.is_active, u.created_at, u.auth_provider, u.google_id
    FROM users u
    JOIN roles r ON u.role_id = r.id
    LEFT JOIN parents p ON u.id = p.id
    WHERE u.id = v_user_id;
END //

CREATE PROCEDURE sp_get_user_for_login(
    IN p_identifier VARCHAR(190)
)
BEGIN
    SELECT u.id, u.name, u.email, u.password_hash, u.auth_provider, u.google_id, u.role_id, r.role_name, u.is_active, p.subscription_tier
    FROM users u
    JOIN roles r ON u.role_id = r.id
    LEFT JOIN parents p ON u.id = p.id
    WHERE u.email = p_identifier OR u.name = p_identifier OR u.username = p_identifier
    LIMIT 1;
END //

CREATE PROCEDURE sp_verify_user_session(
    IN p_user_id INT
)
BEGIN
    SELECT u.id, u.name, u.email, u.role_id, r.role_name, u.is_active
    FROM users u
    JOIN roles r ON u.role_id = r.id
    WHERE u.id = p_user_id AND u.is_active = 1
    LIMIT 1;
END //

CREATE PROCEDURE sp_get_child_for_login(
    IN p_student_id INT,
    IN p_parent_id INT
)
BEGIN
    SELECT s.id, s.parent_id, s.pin_hash, s.avatar, s.class_grade, s.target_board, s.daily_exams_taken_today
    FROM students s
    WHERE s.id = p_student_id AND s.parent_id = p_parent_id
    LIMIT 1;
END //

CREATE PROCEDURE sp_save_refresh_token(
    IN p_user_id INT,
    IN p_token_hash VARCHAR(255),
    IN p_expires_at DATETIME
)
BEGIN
    INSERT INTO refresh_tokens (user_id, token_hash, expires_at, revoked)
    VALUES (p_user_id, p_token_hash, p_expires_at, 0);
END //

CREATE PROCEDURE sp_validate_and_rotate_refresh_token(
    IN p_token_hash VARCHAR(255)
)
BEGIN
    DECLARE v_token_id INT;
    DECLARE v_user_id INT;

    SELECT id, user_id INTO v_token_id, v_user_id
    FROM refresh_tokens
    WHERE token_hash = p_token_hash AND revoked = 0 AND expires_at > NOW()
    LIMIT 1;

    IF v_token_id IS NOT NULL THEN
        UPDATE refresh_tokens SET revoked = 1 WHERE id = v_token_id;

        SELECT u.id, u.name, u.email, r.role_name, u.is_active
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.id = v_user_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TOKEN_EXPIRED_OR_REVOKED';
    END IF;
END //

CREATE PROCEDURE sp_revoke_refresh_token(
    IN p_token_hash VARCHAR(255)
)
BEGIN
    UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = p_token_hash;
END //

CREATE PROCEDURE sp_get_role_menu_permissions(
    IN p_role_name VARCHAR(50)
)
BEGIN
    SELECT m.id, m.page_name, m.page_route, m.icon, m.menu_order, m.is_active
    FROM role_page_access m
    JOIN roles r ON m.role_id = r.id
    WHERE UPPER(r.role_name) = UPPER(p_role_name) AND m.is_active = 1
    ORDER BY m.menu_order ASC;
END //

CREATE PROCEDURE sp_get_registration_roles()
BEGIN
    SELECT 
        id,
        role_name,
        is_active,
        CASE 
            WHEN UPPER(role_name) = 'PARENT' THEN 'Parent (Family & Guardian)'
            WHEN UPPER(role_name) = 'TEACHER' THEN 'Teacher (School Educator / Tutor)'
            ELSE role_name
        END AS display_name,
        CASE 
            WHEN UPPER(role_name) = 'PARENT' THEN 'Manage multiple child sub-accounts and monitor academic diagnostics.'
            WHEN UPPER(role_name) = 'TEACHER' THEN 'Communicate with parents, review student dossiers, and track classes.'
            ELSE 'User account'
        END AS description,
        CASE 
            WHEN UPPER(role_name) = 'PARENT' THEN '👨‍👩‍👧'
            WHEN UPPER(role_name) = 'TEACHER' THEN '🧑‍🏫'
            ELSE '👤'
        END AS icon
    FROM roles
    WHERE UPPER(role_name) IN ('PARENT', 'TEACHER') AND is_active = 1
    ORDER BY id ASC;
END //

CREATE PROCEDURE sp_get_child_registration_masters()
BEGIN
    SELECT 
        (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'name', board_name, 'description', description)) FROM board_master WHERE is_active = 1) AS boards,
        (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'name', class_name)) FROM class_master WHERE is_active = 1) AS classes;
END //

CREATE PROCEDURE sp_add_child_account(
    IN p_parent_id INT,
    IN p_name VARCHAR(150),
    IN p_email VARCHAR(190),
    IN p_password_hash VARCHAR(255),
    IN p_class_grade VARCHAR(20),
    IN p_target_board VARCHAR(20),
    IN p_school_name VARCHAR(190),
    IN p_avatar VARCHAR(20)
)
BEGIN
    DECLARE v_student_user_id INT;
    DECLARE v_student_role_id INT;
    DECLARE v_current_children_count INT;
    DECLARE v_subscription_tier VARCHAR(30);
    DECLARE v_max_children VARCHAR(20);
    DECLARE v_final_email VARCHAR(190);

    SELECT IFNULL(subscription_tier, 'free') INTO v_subscription_tier 
    FROM parents WHERE id = p_parent_id LIMIT 1;

    SELECT max_children INTO v_max_children 
    FROM subscription_plans WHERE id = v_subscription_tier LIMIT 1;

    SELECT COUNT(*) INTO v_current_children_count 
    FROM students WHERE parent_id = p_parent_id;

    IF v_max_children IS NOT NULL AND v_max_children != 'unlimited' AND v_current_children_count >= CAST(v_max_children AS SIGNED) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CHILD_LIMIT_REACHED';
    END IF;

    SELECT id INTO v_student_role_id FROM roles WHERE UPPER(role_name) = 'STUDENT' LIMIT 1;
    IF v_student_role_id IS NULL THEN
        SET v_student_role_id = 1;
    END IF;

    SET v_final_email = TRIM(p_email);
    IF v_final_email IS NULL OR v_final_email = '' THEN
        SELECT email INTO v_final_email FROM users WHERE id = p_parent_id LIMIT 1;
    END IF;

    INSERT INTO users (name, email, password_hash, role_id, auth_provider, is_active, created_at, updated_at)
    VALUES (p_name, v_final_email, p_password_hash, v_student_role_id, 'EMAIL', 1, NOW(), NOW());

    SET v_student_user_id = LAST_INSERT_ID();

    INSERT INTO students (
        id, parent_id, avatar, class_grade, target_board, school_name, pin_hash, 
        daily_exams_taken_today, total_exams_taken, average_score, streak_days, xp, level, created_at, updated_at
    )
    VALUES (
        v_student_user_id, p_parent_id, IFNULL(p_avatar, '👦'), p_class_grade, p_target_board, p_school_name, p_password_hash,
        0, 0, 0.00, 0, 250, 1, NOW(), NOW()
    );

    SELECT 
        s.id, 
        u.name, 
        u.email, 
        s.parent_id, 
        s.avatar, 
        s.class_grade, 
        s.target_board, 
        s.school_name, 
        s.daily_exams_taken_today, 
        s.total_exams_taken, 
        s.average_score, 
        s.streak_days, 
        s.xp, 
        s.level, 
        s.created_at
    FROM students s
    JOIN users u ON s.id = u.id
    WHERE s.id = v_student_user_id;
END //

CREATE PROCEDURE sp_generate_quick_test_from_db(
    IN p_student_id INT,
    IN p_limit INT
)
BEGIN
    DECLARE v_target_board VARCHAR(50);
    DECLARE v_class_grade VARCHAR(50);
    DECLARE v_board_id INT;
    DECLARE v_class_id INT;
    DECLARE v_req_limit INT;

    SET v_req_limit = IFNULL(p_limit, 5);

    -- 1. Fetch student info
    SELECT target_board, class_grade INTO v_target_board, v_class_grade
    FROM students
    WHERE id = p_student_id;

    -- 2. Resolve board_id and class_id
    SELECT id INTO v_board_id FROM board_master WHERE LOWER(TRIM(board_name)) = LOWER(TRIM(v_target_board)) LIMIT 1;
    SELECT id INTO v_class_id FROM class_master WHERE LOWER(TRIM(class_name)) = LOWER(TRIM(v_class_grade)) LIMIT 1;

    -- If student belongs to Kids category (Class 1 to 4)
    IF LOWER(TRIM(v_class_grade)) IN ('class 1', 'class 2', 'class 3', 'class 4') THEN
        SELECT 
            q.id AS question_id,
            q.question AS question_text,
            q.options,
            q.correct_answer,
            q.explanation,
            1 AS marks,
            'MCQ' AS question_type,
            COALESCE(dl.difficulty_level_name, 'simple') AS difficulty,
            s.subject_name,
            ch.chapter_name,
            t.topic_name,
            b.board_name,
            c.class_name
        FROM question_master q
        JOIN topic_master t ON q.topic_id = t.id
        JOIN chapter_master ch ON t.chapter_id = ch.id
        JOIN subject_master s ON ch.subject_id = s.id
        JOIN board_master b ON s.board_id = b.id
        JOIN class_master c ON s.class_id = c.id
        JOIN question_type_master qt ON q.question_type_id = qt.id
        LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
        WHERE q.is_active = 1
          AND qt.question_type_name = 'MCQ'
          AND q.marks = 1
          AND (s.class_id = v_class_id OR v_class_id IS NULL)
        ORDER BY 
          CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id THEN 1
               WHEN s.class_id = v_class_id THEN 2
               WHEN s.board_id = v_board_id THEN 3
               ELSE 4 END,
          RAND()
        LIMIT v_req_limit;
    ELSE
        -- Class 5 to 12 (10 Questions, 15 marks total)
        (
            SELECT 
                q.id AS question_id,
                q.question AS question_text,
                q.options,
                q.correct_answer,
                q.explanation,
                1 AS marks,
                COALESCE(qt.question_type_name, 'MCQ') AS question_type,
                COALESCE(dl.difficulty_level_name, 'medium') AS difficulty,
                s.subject_name,
                ch.chapter_name,
                t.topic_name,
                b.board_name,
                c.class_name
            FROM question_master q
            JOIN topic_master t ON q.topic_id = t.id
            JOIN chapter_master ch ON t.chapter_id = ch.id
            JOIN subject_master s ON ch.subject_id = s.id
            JOIN board_master b ON s.board_id = b.id
            JOIN class_master c ON s.class_id = c.id
            LEFT JOIN question_type_master qt ON q.question_type_id = qt.id
            LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
            WHERE q.is_active = 1
              AND q.marks = 1
            ORDER BY 
              CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id THEN 1
                   WHEN s.class_id = v_class_id THEN 2
                   WHEN s.board_id = v_board_id THEN 3
                   ELSE 4 END,
              RAND()
            LIMIT 5
        )
        UNION ALL
        (
            SELECT 
                q.id AS question_id,
                q.question AS question_text,
                q.options,
                q.correct_answer,
                q.explanation,
                2 AS marks,
                COALESCE(qt.question_type_name, 'SAQ') AS question_type,
                COALESCE(dl.difficulty_level_name, 'medium') AS difficulty,
                s.subject_name,
                ch.chapter_name,
                t.topic_name,
                b.board_name,
                c.class_name
            FROM question_master q
            JOIN topic_master t ON q.topic_id = t.id
            JOIN chapter_master ch ON t.chapter_id = ch.id
            JOIN subject_master s ON ch.subject_id = s.id
            JOIN board_master b ON s.board_id = b.id
            JOIN class_master c ON s.class_id = c.id
            LEFT JOIN question_type_master qt ON q.question_type_id = qt.id
            LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
            WHERE q.is_active = 1
              AND q.marks = 2
            ORDER BY 
              CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id THEN 1
                   WHEN s.class_id = v_class_id THEN 2
                   WHEN s.board_id = v_board_id THEN 3
                   ELSE 4 END,
              RAND()
            LIMIT 5
        )
        ORDER BY RAND();
    END IF;
END //

CREATE PROCEDURE sp_generate_exam_from_db(
    IN p_board VARCHAR(50),
    IN p_class_grade VARCHAR(50),
    IN p_subject VARCHAR(50),
    IN p_difficulty VARCHAR(50)
)
BEGIN
    DECLARE v_board_id INT;
    DECLARE v_class_id INT;
    DECLARE v_is_kids TINYINT(1) DEFAULT 0;

    -- 1. Match board_id
    SELECT id INTO v_board_id 
    FROM board_master 
    WHERE LOWER(TRIM(board_name)) = LOWER(TRIM(p_board))
       OR (LOWER(TRIM(p_board)) IN ('wbbse', 'wb') AND LOWER(TRIM(board_name)) = 'wbbse')
       OR (LOWER(TRIM(p_board)) = 'wbchse' AND LOWER(TRIM(board_name)) = 'wbchse')
    LIMIT 1;

    -- 2. Match class_id
    SELECT id INTO v_class_id 
    FROM class_master 
    WHERE LOWER(TRIM(class_name)) = LOWER(TRIM(p_class_grade))
       OR LOWER(TRIM(class_name)) = CONCAT('class ', LOWER(TRIM(p_class_grade)))
       OR LOWER(TRIM(REPLACE(class_name, 'Class ', ''))) = LOWER(TRIM(REPLACE(p_class_grade, 'Class ', '')))
    LIMIT 1;

    -- Check if kids class (Class 1 to 4)
    IF LOWER(TRIM(p_class_grade)) IN ('class 1', 'class 2', 'class 3', 'class 4', '1', '2', '3', '4') THEN
        SET v_is_kids = 1;
    END IF;

    -- Kids: 5 Questions (All MCQ of 1 Mark = 5 Marks)
    IF v_is_kids = 1 THEN
        SELECT 
            q.id AS question_id,
            q.question AS question_text,
            q.options,
            q.correct_answer,
            q.explanation,
            1 AS marks,
            'MCQ' AS question_type,
            COALESCE(dl.difficulty_level_name, 'simple') AS difficulty,
            s.subject_name,
            ch.chapter_name,
            t.topic_name,
            b.board_name,
            c.class_name
        FROM question_master q
        JOIN topic_master t ON q.topic_id = t.id
        JOIN chapter_master ch ON t.chapter_id = ch.id
        JOIN subject_master s ON ch.subject_id = s.id
        JOIN board_master b ON s.board_id = b.id
        JOIN class_master c ON s.class_id = c.id
        JOIN question_type_master qt ON q.question_type_id = qt.id
        LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
        WHERE q.is_active = 1
          AND qt.question_type_name = 'MCQ'
          AND q.marks = 1
          AND (s.class_id = v_class_id OR v_class_id IS NULL)
        ORDER BY 
          CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 1
               WHEN s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 2
               WHEN s.class_id = v_class_id THEN 3
               WHEN s.board_id = v_board_id THEN 4
               ELSE 5 END,
          RAND()
        LIMIT 5;
    ELSE
        -- Class 5 to 12 (15 Marks: 5 MCQ of 1 Mark + 5 SAQ of 2 Marks)
        (
            SELECT 
                q.id AS question_id,
                q.question AS question_text,
                q.options,
                q.correct_answer,
                q.explanation,
                1 AS marks,
                'MCQ' AS question_type,
                COALESCE(dl.difficulty_level_name, 'medium') AS difficulty,
                s.subject_name,
                ch.chapter_name,
                t.topic_name,
                b.board_name,
                c.class_name
            FROM question_master q
            JOIN topic_master t ON q.topic_id = t.id
            JOIN chapter_master ch ON t.chapter_id = ch.id
            JOIN subject_master s ON ch.subject_id = s.id
            JOIN board_master b ON s.board_id = b.id
            JOIN class_master c ON s.class_id = c.id
            JOIN question_type_master qt ON q.question_type_id = qt.id
            LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
            WHERE q.is_active = 1
              AND qt.question_type_name = 'MCQ'
              AND q.marks = 1
              AND (s.class_id = v_class_id OR v_class_id IS NULL)
            ORDER BY 
              CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 1
                   WHEN s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 2
                   WHEN s.class_id = v_class_id THEN 3
                   WHEN s.board_id = v_board_id THEN 4
                   ELSE 5 END,
              RAND()
            LIMIT 5
        )
        UNION ALL
        (
            SELECT 
                q.id AS question_id,
                q.question AS question_text,
                q.options,
                q.correct_answer,
                q.explanation,
                2 AS marks,
                'SAQ' AS question_type,
                COALESCE(dl.difficulty_level_name, 'medium') AS difficulty,
                s.subject_name,
                ch.chapter_name,
                t.topic_name,
                b.board_name,
                c.class_name
            FROM question_master q
            JOIN topic_master t ON q.topic_id = t.id
            JOIN chapter_master ch ON t.chapter_id = ch.id
            JOIN subject_master s ON ch.subject_id = s.id
            JOIN board_master b ON s.board_id = b.id
            JOIN class_master c ON s.class_id = c.id
            JOIN question_type_master qt ON q.question_type_id = qt.id
            LEFT JOIN difficulty_level_master dl ON q.difficulty_level_id = dl.id
            WHERE q.is_active = 1
              AND qt.question_type_name = 'SAQ'
              AND q.marks = 2
              AND (s.class_id = v_class_id OR v_class_id IS NULL)
            ORDER BY 
              CASE WHEN s.board_id = v_board_id AND s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 1
                   WHEN s.class_id = v_class_id AND LOWER(TRIM(s.subject_name)) = LOWER(TRIM(p_subject)) THEN 2
                   WHEN s.class_id = v_class_id THEN 3
                   WHEN s.board_id = v_board_id THEN 4
                   ELSE 5 END,
              RAND()
            LIMIT 5
        );
    END IF;
END //

DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;
