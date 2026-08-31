-- ============================================================
-- ACUGRADE AI — MySQL SCHEMA WITH RBAC & STORED PROCEDURES
-- Charset: utf8mb4 (Board/subject text contains non-ASCII symbols)
-- Engine: InnoDB everywhere for FK support
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. ROLES & DYNAMIC PAGE ACCESS
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- 2. USERS & AUTH
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(150) NOT NULL,
  email         VARCHAR(190) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role_id       INT          NOT NULL,
  is_active     TINYINT(1)   NOT NULL DEFAULT 1,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by    INT          NULL,
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by    INT          NULL,
  UNIQUE KEY uq_users_email (email),
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

-- ------------------------------------------------------------
-- 3. PARENT / STUDENT / TEACHER PROFILES
-- ------------------------------------------------------------
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
  id                     INT          NOT NULL PRIMARY KEY, -- == users.id
  parent_id              INT          NOT NULL,
  teacher_id             INT          NULL,
  avatar                 VARCHAR(20)  NOT NULL DEFAULT '🧑‍🎓',
  class_grade            VARCHAR(20)  NOT NULL,
  target_board           VARCHAR(20)  NOT NULL,
  school_name            VARCHAR(190) NULL,
  pin_hash               VARCHAR(255) NOT NULL,
  daily_exams_taken_today INT         NOT NULL DEFAULT 0,
  last_exam_date         DATE         NULL,
  total_exams_taken      INT          NOT NULL DEFAULT 0,
  average_score          DECIMAL(4,2) NOT NULL DEFAULT 0.00,
  streak_days            INT          NOT NULL DEFAULT 0,
  xp                     INT          NOT NULL DEFAULT 250,
  level                  INT          NOT NULL DEFAULT 1,
  created_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_students_user    FOREIGN KEY (id)         REFERENCES users(id)    ON DELETE CASCADE,
  CONSTRAINT fk_students_parent  FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
  CONSTRAINT fk_students_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
  KEY idx_students_parent (parent_id),
  KEY idx_students_teacher (teacher_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. CURRICULUM / RUNBOOKS (K-GRAPH SOURCE NODES)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS runbooks (
  id                      CHAR(36)     NOT NULL PRIMARY KEY,
  board                   VARCHAR(20)  NOT NULL,
  class_grade             VARCHAR(20)  NOT NULL,
  subject                 VARCHAR(40)  NOT NULL,
  chapter_name            VARCHAR(190) NOT NULL,
  core_concepts           JSON NOT NULL,
  key_formulas_or_rules   JSON NOT NULL,
  common_traps            JSON NOT NULL,
  curated_reference_urls  JSON NOT NULL,
  sample_question_archetypes JSON NOT NULL,
  difficulty_calibration  JSON NOT NULL,
  status                  ENUM('DRAFT','PUBLISHED','ARCHIVED') NOT NULL DEFAULT 'PUBLISHED',
  version                 INT NOT NULL DEFAULT 1,
  created_by              INT NULL,
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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

-- ------------------------------------------------------------
-- 5. EXAMS / QUESTIONS / SUBMISSIONS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exams (
  id                     CHAR(36)     NOT NULL PRIMARY KEY,
  student_id             INT          NOT NULL,
  title                  VARCHAR(255) NOT NULL,
  board                  VARCHAR(20)  NOT NULL,
  class_grade            VARCHAR(20)  NOT NULL,
  subject                VARCHAR(40)  NOT NULL,
  difficulty             ENUM('simple','medium','hard') NOT NULL,
  total_marks            INT NOT NULL DEFAULT 10,
  question_count         INT NOT NULL DEFAULT 10,
  time_limit_minutes     INT NOT NULL DEFAULT 15,
  rag_knowledge_nodes_used JSON NULL,
  source                 ENUM('mistral-rag','rag-engine-curated') NOT NULL,
  status                 ENUM('GENERATED','IN_PROGRESS','SUBMITTED','EXPIRED') NOT NULL DEFAULT 'GENERATED',
  created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_exams_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  KEY idx_exams_student (student_id),
  KEY idx_exams_created (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS questions (
  id               CHAR(36)     NOT NULL PRIMARY KEY,
  exam_id          CHAR(36)     NOT NULL,
  question_number  INT NOT NULL,
  type             ENUM('mcq','objective','numerical','logical') NOT NULL,
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
  marks_obtained        INT NOT NULL,
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
  marks_awarded            INT NOT NULL,
  misconception_identified VARCHAR(255) NULL,
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

-- ------------------------------------------------------------
-- 6. MASTERY / MISCONCEPTIONS / LEARNING PATH
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mastery (
  id             CHAR(36)     NOT NULL PRIMARY KEY,
  student_id     INT          NOT NULL,
  topic          VARCHAR(190) NOT NULL,
  mastery_score  DECIMAL(5,2) NOT NULL DEFAULT 0,
  confidence     DECIMAL(5,2) NOT NULL DEFAULT 0,
  attempt_count  INT NOT NULL DEFAULT 0,
  correct_count  INT NOT NULL DEFAULT 0,
  status         ENUM('NOT_STARTED','LEARNING','DEVELOPING','MASTERED','CRITICAL_GAP') NOT NULL DEFAULT 'NOT_STARTED',
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

-- ------------------------------------------------------------
-- 7. GAMIFICATION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS badges (
  id               VARCHAR(60)  NOT NULL PRIMARY KEY,
  title            VARCHAR(150) NOT NULL,
  description      VARCHAR(255) NOT NULL,
  icon             VARCHAR(20)  NOT NULL,
  tier             ENUM('bronze','silver','gold','diamond') NOT NULL,
  category         ENUM('mastery','streak','score','speed','explorer') NOT NULL,
  xp_reward        INT NOT NULL DEFAULT 0,
  requirement_text VARCHAR(255) NOT NULL
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

-- ------------------------------------------------------------
-- 8. PARENT-TEACHER COMMUNICATION
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- 9. SUBSCRIPTIONS & PLANS
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- 10. AUDIT LOG
-- ------------------------------------------------------------
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
-- 11. STORED PROCEDURES
-- ============================================================
DROP PROCEDURE IF EXISTS sp_register_parent;
DROP PROCEDURE IF EXISTS sp_get_user_for_login;
DROP PROCEDURE IF EXISTS sp_verify_user_session;
DROP PROCEDURE IF EXISTS sp_get_child_for_login;
DROP PROCEDURE IF EXISTS sp_save_refresh_token;
DROP PROCEDURE IF EXISTS sp_validate_and_rotate_refresh_token;
DROP PROCEDURE IF EXISTS sp_revoke_refresh_token;
DROP PROCEDURE IF EXISTS sp_get_role_menu_permissions;

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

        INSERT INTO users (name, email, password_hash, role_id, is_active, created_at, updated_at)
        VALUES (p_name, p_email, p_password_hash, v_role_id, 1, NOW(), NOW());

        SET v_user_id = LAST_INSERT_ID();
        
        IF UPPER(p_role_name) = 'TEACHER' THEN
            INSERT INTO teachers (id, role_title, subject, school_name, verified)
            VALUES (v_user_id, 'Subject Teacher', 'General', 'Partner School', 1);
        ELSE
            INSERT INTO parents (id, subscription_tier) VALUES (v_user_id, 'free');
        END IF;

        SELECT u.id, u.name, u.email, u.role_id, r.role_name, IFNULL(p.subscription_tier, 'free') AS subscription_tier, u.is_active, u.created_at
        FROM users u
        JOIN roles r ON u.role_id = r.id
        LEFT JOIN parents p ON u.id = p.id
        WHERE u.id = v_user_id;
    END IF;
END //

CREATE PROCEDURE sp_get_user_for_login(
    IN p_identifier VARCHAR(190)
)
BEGIN
    SELECT u.id, u.name, u.email, u.password_hash, u.role_id, r.role_name, u.is_active, p.subscription_tier
    FROM users u
    JOIN roles r ON u.role_id = r.id
    LEFT JOIN parents p ON u.id = p.id
    WHERE u.email = p_identifier OR u.name = p_identifier
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

DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;
