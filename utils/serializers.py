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
    evaluations_list = []
    if submission.evaluations:
        for ev in submission.evaluations:
            q = ev.question if hasattr(ev, 'question') and ev.question else None
            evaluations_list.append({
                "questionId": ev.question_id,
                "questionNumber": q.question_number if q else 1,
                "type": q.type if q else "mcq",
                "questionText": q.question_text if q else "",
                "options": q.options if q else [],
                "studentAnswer": ev.student_answer,
                "correctAnswer": q.correct_answer if q else "",
                "isCorrect": ev.is_correct,
                "marksAwarded": ev.marks_awarded,
                "explanation": q.explanation if q else "",
                "misconceptionIdentified": ev.misconception_identified,
                "referenceLinks": q.reference_links if q else [],
                "topic": q.topic if q else (submission.exam.subject if submission.exam else "General"),
            })

    analysis_dict = {
        "overallBand": "Proficient",
        "masteryScorePercentage": float(submission.accuracy_percentage or 0),
        "strengths": ["Foundational problem-solving", "Conceptual recall"],
        "areasToImprove": ["Timed accuracy", "Advanced HOTS questions"],
        "kGraphInsights": [],
        "evolutionaryRoadmap": "Continue daily diagnostic sprint practice to achieve full topic mastery.",
        "encouragementNote": "Solid diagnostic performance. Focus on identified remediation areas to maximize scores.",
        "recommendedNextExam": {
            "board": submission.exam.board if submission.exam else "CBSE",
            "classGrade": submission.exam.class_grade if submission.exam else "Class 10",
            "subject": submission.exam.subject if submission.exam else "Mathematics",
            "difficulty": "medium",
            "reason": "Reinforce conceptual foundations from diagnostic insights."
        },
        "curatedStudyLinks": [],
    }

    if submission.analysis:
        a = submission.analysis
        analysis_dict = {
            "overallBand": a.overall_band,
            "masteryScorePercentage": float(a.mastery_score_percentage or submission.accuracy_percentage or 0),
            "strengths": a.strengths or ["Core understanding"],
            "areasToImprove": a.areas_to_improve or ["Targeted practice"],
            "kGraphInsights": a.k_graph_insights or [],
            "evolutionaryRoadmap": a.evolutionary_roadmap or "Follow adaptive learning path.",
            "encouragementNote": a.encouragement_note or "Great effort on completing the diagnostic exam!",
            "recommendedNextExam": a.recommended_next_exam or {
                "board": submission.exam.board if submission.exam else "CBSE",
                "classGrade": submission.exam.class_grade if submission.exam else "Class 10",
                "subject": submission.exam.subject if submission.exam else "Mathematics",
                "difficulty": "medium",
                "reason": "Adaptive progression"
            },
            "curatedStudyLinks": a.curated_study_links or [],
        }

    return {
        "id": submission.id,
        "examId": submission.exam_id,
        "studentId": submission.student_id,
        "studentName": submission.student.user.name if (submission.student and submission.student.user) else "Student",
        "examTitle": submission.exam.title if submission.exam else "10-Mark Diagnostic Exam",
        "board": submission.exam.board if submission.exam else "CBSE",
        "classGrade": submission.exam.class_grade if submission.exam else "Class 10",
        "subject": submission.exam.subject if submission.exam else "Mathematics",
        "difficulty": submission.exam.difficulty if submission.exam else "medium",
        "answers": submission.answers or {},
        "marksObtained": submission.marks_obtained,
        "totalMarks": submission.total_marks or 10,
        "accuracyPercentage": float(submission.accuracy_percentage or 0),
        "timeTakenSeconds": submission.time_taken_seconds or 0,
        "submittedAt": submission.submitted_at.isoformat() if submission.submitted_at else "",
        "evaluations": evaluations_list,
        "analysis": analysis_dict,
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
