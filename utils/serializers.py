"""Serializers that produce the exact camelCase shapes the frontend's
types.ts already defines, so the React components need no restructuring."""
from model.models import Student, ExamSubmission, LearningPathNode, Badge, Misconception


def student_to_child_account(student: Student, badge_ids: list[str] | None = None) -> dict:
    return {
        "id": student.id,
        "parentId": student.parent_id,
        "name": student.user.name if student.user else "",
        "avatar": student.avatar,
        "classGrade": student.class_grade,
        "targetBoard": student.target_board,
        "schoolName": student.school_name,
        "dailyExamsTakenToday": student.daily_exams_taken_today,
        "lastExamDate": student.last_exam_date.isoformat() if student.last_exam_date else None,
        "totalExamsTaken": student.total_exams_taken,
        "averageScore": float(student.average_score or 0),
        "streakDays": student.streak_days,
        "createdAt": student.created_at.isoformat(),
        "xp": student.xp,
        "level": student.level,
        "earnedBadgeIds": badge_ids or [],
    }


def submission_to_dict(submission: ExamSubmission) -> dict:
    return {
        "id": submission.id,
        "examId": submission.exam_id,
        "studentId": submission.student_id,
        "answers": submission.answers,
        "marksObtained": submission.marks_obtained,
        "totalMarks": submission.total_marks,
        "accuracyPercentage": float(submission.accuracy_percentage),
        "timeTakenSeconds": submission.time_taken_seconds,
        "submittedAt": submission.submitted_at.isoformat(),
    }


def learning_path_node_to_dict(node: LearningPathNode) -> dict:
    return {
        "id": node.id,
        "topic": node.topic,
        "chapterName": node.chapter_name,
        "subject": node.subject,
        "classGrade": node.class_grade,
        "board": node.board,
        "status": node.status,
        "masteryPercentage": float(node.mastery_percentage or 0),
        "level": node.level,
        "prerequisites": node.prerequisites or [],
        "keyConcepts": node.key_concepts or [],
        "commonMisconceptions": node.common_misconceptions or [],
        "curatedResources": node.curated_resources or [],
        "practiceExamConfig": node.practice_exam_config or {},
        "recommendedReason": node.recommended_reason,
    }


def badge_to_dict(badge: Badge) -> dict:
    return {
        "id": badge.id,
        "title": badge.title,
        "description": badge.description,
        "icon": badge.icon,
        "tier": badge.tier,
        "category": badge.category,
        "xpReward": badge.xp_reward,
        "requirementText": badge.requirement_text,
    }


def runbook_to_dict(rb) -> dict:
    return {
        "id": rb.id,
        "board": rb.board,
        "classGrade": rb.class_grade,
        "subject": rb.subject,
        "chapterName": rb.chapter_name,
        "coreConcepts": rb.core_concepts,
        "keyFormulasOrRules": rb.key_formulas_or_rules,
        "commonTraps": rb.common_traps,
        "curatedReferenceUrls": rb.curated_reference_urls,
        "sampleQuestionArchetypes": rb.sample_question_archetypes,
        "difficultyCalibration": rb.difficulty_calibration,
        "status": rb.status,
        "lastUpdated": rb.updated_at.date().isoformat() if rb.updated_at else None,
    }


def misconception_to_dict(m: Misconception) -> dict:
    return {
        "id": m.id,
        "topic": m.topic,
        "description": m.description,
        "evidence": m.evidence,
        "severity": m.severity,
        "status": m.status,
    }
