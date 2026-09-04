import json
import uuid
from datetime import date, datetime

from flask import request, g
from sqlalchemy import text

from database.dbConnection import get_session
from helper import diagnostic_engine, exam_generator, gamification_engine, mastery_engine, misconception_engine
from helper.adaptive_learning_engine import update_learning_path_after_submission
from helper.evaluation_engine import evaluate_exam
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import assert_owns_student
from model.models import Exam, ExamSubmission, QuestionEvaluation, DiagnosticAnalysis, Student, Parent, SubscriptionPlan
from utils.errors import AppError, NotFoundError, QuotaExceededError, ValidationError
from utils.response import success
from utils.serializers import submission_to_dict
from utils.validators import require_fields, validate_board, validate_class_grade, validate_subject, validate_difficulty



def _resolve_student_for_request(session, payload: dict) -> Student:
    """A parent generates an exam on behalf of a named child; a student
    token (from /auth/child-login) generates it for themselves."""
    if g.current_user_role == "STUDENT":
        s_id = int(g.current_user_id) if str(g.current_user_id).isdigit() else g.current_user_id
        student = session.get(Student, s_id)
        if not student:
            raise NotFoundError("Student not found")
        return student

    require_fields(payload, ["studentId"])
    return assert_owns_student(session, payload["studentId"], g.current_user_id)


def _reset_daily_quota_if_new_day(student: Student):
    today = date.today()
    if student.last_exam_date != today:
        student.daily_exams_taken_today = 0


@token_required
def generate_exam():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["board", "subject", "difficulty"])
    validate_board(payload["board"])
    if payload.get("classGrade"):
        validate_class_grade(payload["classGrade"])
    validate_subject(payload["subject"])
    validate_difficulty(payload["difficulty"])

    with get_session() as session:
        student = _resolve_student_for_request(session, payload)
        _reset_daily_quota_if_new_day(student)

        # Quota is re-checked here server-side
        parent = session.get(Parent, student.parent_id)
        plan = session.get(SubscriptionPlan, parent.subscription_tier) if parent else None
        if plan and plan.daily_exam_limit != "unlimited":
            if student.daily_exams_taken_today >= int(plan.daily_exam_limit):
                raise QuotaExceededError(
                    f"Daily exam limit ({plan.daily_exam_limit}) reached for the {parent.subscription_tier} plan"
                )

        exam = exam_generator.generate_exam(
            session,
            student_id=student.id,
            student_name=student.user.name if student.user else "Student",
            board=payload["board"],
            class_grade=payload.get("classGrade", student.class_grade),
            subject=payload["subject"],
            difficulty=payload["difficulty"],
        )

        student.daily_exams_taken_today = (student.daily_exams_taken_today or 0) + 1
        student.last_exam_date = date.today()

        return success(
            {"exam": exam_generator.exam_to_public_dict(exam)},
            201,
            source=exam.source,
        )


@token_required
def generate_quick_test():
    """Generates a random 10-question Quick Diagnostic Test directly from DB
    via Stored Procedure matching the student's registered Curriculum Board & Class Grade."""
    payload = request.get_json(force=True, silent=True) or {}
    if not payload.get("studentId") and request.args.get("studentId"):
        payload["studentId"] = request.args.get("studentId")

    with get_session() as session:
        student = _resolve_student_for_request(session, payload)
        _reset_daily_quota_if_new_day(student)

        # Quota check
        parent = session.get(Parent, student.parent_id)
        plan = session.get(SubscriptionPlan, parent.subscription_tier) if parent else None
        if plan and plan.daily_exam_limit != "unlimited":
            if (student.daily_exams_taken_today or 0) >= int(plan.daily_exam_limit):
                raise QuotaExceededError(
                    f"Daily exam limit ({plan.daily_exam_limit}) reached for the {parent.subscription_tier} plan"
                )

        is_kid = (student.class_grade or '').strip().lower() in ['class 1', 'class 2', 'class 3', 'class 4']
        default_limit = 5 if is_kid else 10
        limit = int(payload.get("limit", default_limit))
        sp_rows = session.execute(
            text("CALL sp_generate_quick_test_from_db(:student_id, :limit)"),
            {"student_id": student.id, "limit": limit}
        ).mappings().fetchall()

        if not sp_rows:
            raise NotFoundError("No diagnostic questions found in database for this student")

        total_exam_marks = sum(int(r.get("marks") or 1) for r in sp_rows)
        primary_subject = sp_rows[0].get("subject_name") or "General Assessment"
        if is_kid:
            title = f"{student.class_grade} {student.target_board} Adventure Challenge ({total_exam_marks} Marks)"
            time_limit = 10
        else:
            title = f"{student.class_grade} {student.target_board} Quick Diagnostic Assessment ({total_exam_marks} Marks)"
            time_limit = 15

        from model.models import Question
        exam = Exam(
            id=str(uuid.uuid4()),
            student_id=student.id,
            title=title,
            board=student.target_board,
            class_grade=student.class_grade,
            subject=primary_subject,
            difficulty="simple" if is_kid else "medium",
            total_marks=total_exam_marks,
            question_count=len(sp_rows),
            time_limit_minutes=time_limit,
            rag_knowledge_nodes_used=list({r.get("chapter_name") for r in sp_rows if r.get("chapter_name")}),
            source="rag-engine-curated",
            status="GENERATED",
            created_at=datetime.utcnow(),
        )
        session.add(exam)
        session.flush()

        for idx, row in enumerate(sp_rows):
            raw_options = row.get("options")
            parsed_options = None
            if isinstance(raw_options, str):
                try:
                    parsed_options = json.loads(raw_options)
                except Exception:
                    parsed_options = [raw_options]
            elif isinstance(raw_options, list):
                parsed_options = raw_options

            # Map type to valid Enum: "mcq", "objective", "numerical", "logical"
            raw_type = (row.get("question_type") or "").lower()
            if parsed_options and len(parsed_options) > 1:
                q_type = "mcq"
            elif "num" in raw_type or "math" in raw_type:
                q_type = "numerical"
            elif "logic" in raw_type:
                q_type = "logical"
            else:
                q_type = "objective"

            # Map difficulty to valid Enum: "simple", "medium", "hard"
            raw_diff = (row.get("difficulty") or "medium").lower()
            if "easy" in raw_diff or "sim" in raw_diff:
                q_diff = "simple"
            elif "hard" in raw_diff or "adv" in raw_diff:
                q_diff = "hard"
            else:
                q_diff = "medium"

            exam.questions.append(
                Question(
                    id=str(uuid.uuid4()),
                    question_number=idx + 1,
                    type=q_type,
                    question_text=row.get("question_text") or f"Question {idx + 1}",
                    options=parsed_options,
                    correct_answer=str(row.get("correct_answer") or ""),
                    explanation=row.get("explanation") or "Step-by-step diagnostic solution.",
                    difficulty=q_diff,
                    marks=int(row.get("marks") or 1),
                    topic=row.get("topic_name") or primary_subject,
                    reference_links=[],
                    hint=f"Focus on {row.get('topic_name') or primary_subject} fundamentals.",
                )
            )

        student.daily_exams_taken_today = (student.daily_exams_taken_today or 0) + 1
        student.last_exam_date = date.today()
        session.flush()

        return success(
            {
                "exam": exam_generator.exam_to_public_dict(exam),
                "student": {
                    "id": student.id,
                    "name": student.user.name if student.user else "",
                    "avatar": student.avatar,
                    "classGrade": student.class_grade,
                    "targetBoard": student.target_board,
                }
            },
            201,
            source="mysql-stored-procedure"
        )


@token_required
def submit_exam(exam_id):
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["answers"])
    answers = payload["answers"]
    if not isinstance(answers, dict):
        raise ValidationError("'answers' must be an object of {questionId: answerText}")
    time_taken_seconds = max(10, int(payload.get("timeTakenSeconds", 10)))

    with get_session() as session:
        exam = session.get(Exam, exam_id)
        if not exam:
            raise NotFoundError("Exam not found")

        current_uid = int(g.current_user_id) if str(g.current_user_id).isdigit() else g.current_user_id

        if g.current_user_role == "STUDENT" and exam.student_id != current_uid:
            raise AppError("FORBIDDEN", "This exam does not belong to you", 403)
        elif g.current_user_role == "PARENT":
            assert_owns_student(session, exam.student_id, current_uid)

        if exam.status == "SUBMITTED":
            raise AppError("ALREADY_SUBMITTED", "This exam has already been submitted", 409)

        evaluations, marks_obtained = evaluate_exam(exam.questions, answers)
        accuracy_percentage = round((marks_obtained / exam.total_marks) * 100, 2)

        student = session.get(Student, exam.student_id)
        student_name = student.user.name if student and student.user else "Student"

        analysis, analysis_source = diagnostic_engine.generate_diagnostic_analysis(
            exam, marks_obtained, evaluations, time_taken_seconds, student_name
        )

        submission = ExamSubmission(
            id=str(uuid.uuid4()), exam_id=exam.id, student_id=exam.student_id, answers=answers,
            marks_obtained=marks_obtained, total_marks=exam.total_marks,
            accuracy_percentage=accuracy_percentage, time_taken_seconds=time_taken_seconds,
            submitted_at=datetime.utcnow(),
        )
        session.add(submission)
        session.flush()

        for ev in evaluations:
            session.add(
                QuestionEvaluation(
                    id=str(uuid.uuid4()), submission_id=submission.id, question_id=ev["questionId"],
                    student_answer=ev["studentAnswer"], is_correct=ev["isCorrect"],
                    marks_awarded=ev["marksAwarded"], misconception_identified=ev["misconceptionIdentified"],
                )
            )

        session.add(
            DiagnosticAnalysis(
                id=str(uuid.uuid4()), submission_id=submission.id,
                overall_band=analysis["overallBand"], mastery_score_percentage=analysis["masteryScorePercentage"],
                strengths=analysis["strengths"], areas_to_improve=analysis["areasToImprove"],
                k_graph_insights=analysis["kGraphInsights"], evolutionary_roadmap=analysis["evolutionaryRoadmap"],
                encouragement_note=analysis["encouragementNote"],
                recommended_next_exam=analysis["recommendedNextExam"],
                curated_study_links=analysis["curatedStudyLinks"], source=analysis_source,
            )
        )

        exam.status = "SUBMITTED"

        # Server-side XP/badges
        xp_earned = gamification_engine.compute_exam_xp(marks_obtained, time_taken_seconds)
        newly_unlocked_badges = gamification_engine.evaluate_badge_unlocks(
            session, student, marks_obtained, time_taken_seconds, exam.difficulty
        )
        gamification_engine.award_xp(session, student, xp_earned, f"exam:{exam.id}")

        # Rolling average percentage (0-100%) + streak + mastery + misconceptions + learning path.
        updated_total = (student.total_exams_taken or 0) + 1
        student.average_score = round(
            ((float(student.average_score or 0) * (student.total_exams_taken or 0)) + accuracy_percentage) / updated_total, 2
        )
        student.total_exams_taken = updated_total
        student.streak_days = (student.streak_days or 0) + 1

        mastery_engine.update_mastery_from_insights(session, student.id, analysis["kGraphInsights"])
        misconception_engine.record_misconceptions_from_evaluations(session, student.id, evaluations)
        update_learning_path_after_submission(
            session, student.id, exam.subject, marks_obtained, analysis["kGraphInsights"]
        )

        return success({
            "submission": {
                **submission_to_dict(submission),
                "examTitle": exam.title, "board": exam.board, "classGrade": exam.class_grade,
                "subject": exam.subject, "difficulty": exam.difficulty, "studentName": student_name,
                "evaluations": evaluations, "analysis": analysis,
            },
            "xpEarned": xp_earned,
            "newlyUnlockedBadges": newly_unlocked_badges,
        })
