-- ============================================================
-- AcuGrade AI - Curriculum Master Data Seeding Script
-- Seeds Boards, Classes, Subjects, Chapters, Topics & Master Catalogs
-- For all Active Boards: CBSE, ICSE, ISC, WBBSE, WBCHSE, UK-Cambridge, NCERT, NEET, IIT
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. SEED BOARDS & CLASSES
-- ------------------------------------------------------------
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

INSERT INTO question_type_master (id, question_type_name, default_marks, is_active) VALUES
(1, 'MCQ', 1, 1),
(2, 'Objective', 1, 1),
(3, 'SAQ', 2, 1),
(4, 'Numerical', 2, 1),
(5, 'Logical', 2, 1)
ON DUPLICATE KEY UPDATE question_type_name = VALUES(question_type_name), default_marks = VALUES(default_marks), is_active = 1;

INSERT INTO difficulty_level_master (id, difficulty_level_name, is_active) VALUES
(1, 'simple', 1),
(2, 'medium', 1),
(3, 'hard', 1)
ON DUPLICATE KEY UPDATE difficulty_level_name = VALUES(difficulty_level_name), is_active = 1;

-- ------------------------------------------------------------
-- 2. SEED SUBJECTS FOR ALL ACTIVE BOARDS
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
-- 3. SEED DEFAULT CHAPTERS FOR ALL SUBJECTS
-- ------------------------------------------------------------
INSERT INTO chapter_master (subject_id, chapter_name, is_active)
SELECT s.id, CONCAT('General Concepts of ', s.subject_name), 1
FROM subject_master s
WHERE s.is_active = 1
  AND NOT EXISTS (
      SELECT 1 FROM chapter_master ch WHERE ch.subject_id = s.id
  );

-- ------------------------------------------------------------
-- 4. SEED DEFAULT TOPICS FOR ALL CHAPTERS
-- ------------------------------------------------------------
INSERT INTO topic_master (chapter_id, topic_name, is_active)
SELECT ch.id, 'Core Theory & Concepts', 1
FROM chapter_master ch
WHERE ch.is_active = 1
  AND NOT EXISTS (
      SELECT 1 FROM topic_master t WHERE t.chapter_id = ch.id
  );

SET FOREIGN_KEY_CHECKS = 1;
