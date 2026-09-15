-- ============================================================================
-- Stored Procedure: sp_generate_exam_from_db
-- Description: Dynamic 3-Tier Exam Question Generator
-- Tier 1 (Class 1-4): 5 MCQs @ 1 Mark = 5 Marks
-- Tier 2 (Class 5-10): 5 MCQs @ 1M + 5 SAQs @ 2M = 15 Marks
-- Tier 3 (Class 11-12 / NEET / IIT): 10 Questions @ 2 Marks = 20 Marks
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_generate_exam_from_db;

DELIMITER $$

CREATE PROCEDURE sp_generate_exam_from_db(
    IN p_board VARCHAR(50),
    IN p_class_grade VARCHAR(50),
    IN p_subject VARCHAR(100),
    IN p_difficulty VARCHAR(50)
)
BEGIN
    DECLARE v_class_num INT DEFAULT 5;
    DECLARE v_clean_class VARCHAR(50);
    DECLARE v_is_senior BOOLEAN DEFAULT FALSE;
    
    SET v_clean_class = LOWER(TRIM(IFNULL(p_class_grade, 'Class 5')));
    
    IF v_clean_class LIKE '%class 12%' OR v_clean_class LIKE '%12%' OR v_clean_class LIKE '%isc%' OR v_clean_class LIKE '%neet%' OR v_clean_class LIKE '%iit%' OR v_clean_class LIKE '%jee%' THEN
        SET v_class_num = 12;
        SET v_is_senior = TRUE;
    ELSEIF v_clean_class LIKE '%class 11%' OR v_clean_class LIKE '%11%' THEN
        SET v_class_num = 11;
        SET v_is_senior = TRUE;
    ELSEIF v_clean_class LIKE '%class 10%' OR v_clean_class LIKE '%10%' THEN
        SET v_class_num = 10;
    ELSEIF v_clean_class LIKE '%class 9%' OR v_clean_class LIKE '%9%' THEN
        SET v_class_num = 9;
    ELSEIF v_clean_class LIKE '%class 8%' OR v_clean_class LIKE '%8%' THEN
        SET v_class_num = 8;
    ELSEIF v_clean_class LIKE '%class 7%' OR v_clean_class LIKE '%7%' THEN
        SET v_class_num = 7;
    ELSEIF v_clean_class LIKE '%class 6%' OR v_clean_class LIKE '%6%' THEN
        SET v_class_num = 6;
    ELSEIF v_clean_class LIKE '%class 5%' OR v_clean_class LIKE '%5%' THEN
        SET v_class_num = 5;
    ELSEIF v_clean_class LIKE '%class 4%' OR v_clean_class LIKE '%4%' THEN
        SET v_class_num = 4;
    ELSEIF v_clean_class LIKE '%class 3%' OR v_clean_class LIKE '%3%' THEN
        SET v_class_num = 3;
    ELSEIF v_clean_class LIKE '%class 2%' OR v_clean_class LIKE '%2%' THEN
        SET v_class_num = 2;
    ELSEIF v_clean_class LIKE '%class 1%' OR v_clean_class LIKE '%1%' THEN
        SET v_class_num = 1;
    ELSE
        SET v_class_num = 5;
    END IF;

    IF v_class_num >= 1 AND v_class_num <= 4 THEN
        -- Tier 1: Class 1 to 4 -> 5 MCQs @ 1 mark = 5 marks
        SELECT 
            question_id,
            board,
            class_grade,
            subject,
            topic,
            difficulty,
            question_type,
            question_text,
            options_json,
            correct_answer,
            explanation,
            1 AS marks
        FROM question_master
        WHERE LOWER(TRIM(board)) = LOWER(TRIM(p_board))
          AND LOWER(TRIM(class_grade)) = LOWER(TRIM(p_class_grade))
          AND LOWER(TRIM(subject)) = LOWER(TRIM(p_subject))
          AND (p_difficulty IS NULL OR p_difficulty = '' OR LOWER(TRIM(difficulty)) = LOWER(TRIM(p_difficulty)))
          AND LOWER(TRIM(question_type)) = 'mcq'
        ORDER BY RAND()
        LIMIT 5;

    ELSEIF v_class_num >= 5 AND v_class_num <= 10 THEN
        -- Tier 2: Class 5 to 10 -> 5 MCQs (1M) + 5 SAQs (2M) = 15 marks
        (
            SELECT 
                question_id,
                board,
                class_grade,
                subject,
                topic,
                difficulty,
                question_type,
                question_text,
                options_json,
                correct_answer,
                explanation,
                1 AS marks
            FROM question_master
            WHERE LOWER(TRIM(board)) = LOWER(TRIM(p_board))
              AND LOWER(TRIM(class_grade)) = LOWER(TRIM(p_class_grade))
              AND LOWER(TRIM(subject)) = LOWER(TRIM(p_subject))
              AND (p_difficulty IS NULL OR p_difficulty = '' OR LOWER(TRIM(difficulty)) = LOWER(TRIM(p_difficulty)))
              AND LOWER(TRIM(question_type)) = 'mcq'
            ORDER BY RAND()
            LIMIT 5
        )
        UNION ALL
        (
            SELECT 
                question_id,
                board,
                class_grade,
                subject,
                topic,
                difficulty,
                question_type,
                question_text,
                options_json,
                correct_answer,
                explanation,
                2 AS marks
            FROM question_master
            WHERE LOWER(TRIM(board)) = LOWER(TRIM(p_board))
              AND LOWER(TRIM(class_grade)) = LOWER(TRIM(p_class_grade))
              AND LOWER(TRIM(subject)) = LOWER(TRIM(p_subject))
              AND (p_difficulty IS NULL OR p_difficulty = '' OR LOWER(TRIM(difficulty)) = LOWER(TRIM(p_difficulty)))
              AND LOWER(TRIM(question_type)) IN ('saq', 'short_answer', 'descriptive')
            ORDER BY RAND()
            LIMIT 5
        );

    ELSE
        -- Tier 3: Class 11-12 / NEET / IIT -> 10 Questions @ 2 Marks = 20 Marks
        (
            SELECT 
                question_id,
                board,
                class_grade,
                subject,
                topic,
                difficulty,
                question_type,
                question_text,
                options_json,
                correct_answer,
                explanation,
                2 AS marks
            FROM question_master
            WHERE LOWER(TRIM(board)) = LOWER(TRIM(p_board))
              AND LOWER(TRIM(class_grade)) = LOWER(TRIM(p_class_grade))
              AND LOWER(TRIM(subject)) = LOWER(TRIM(p_subject))
              AND (p_difficulty IS NULL OR p_difficulty = '' OR LOWER(TRIM(difficulty)) = LOWER(TRIM(p_difficulty)))
              AND LOWER(TRIM(question_type)) = 'mcq'
            ORDER BY RAND()
            LIMIT 5
        )
        UNION ALL
        (
            SELECT 
                question_id,
                board,
                class_grade,
                subject,
                topic,
                difficulty,
                question_type,
                question_text,
                options_json,
                correct_answer,
                explanation,
                2 AS marks
            FROM question_master
            WHERE LOWER(TRIM(board)) = LOWER(TRIM(p_board))
              AND LOWER(TRIM(class_grade)) = LOWER(TRIM(p_class_grade))
              AND LOWER(TRIM(subject)) = LOWER(TRIM(p_subject))
              AND (p_difficulty IS NULL OR p_difficulty = '' OR LOWER(TRIM(difficulty)) = LOWER(TRIM(p_difficulty)))
              AND LOWER(TRIM(question_type)) IN ('saq', 'short_answer', 'descriptive')
            ORDER BY RAND()
            LIMIT 5
        );
    END IF;
END $$

DELIMITER ;
