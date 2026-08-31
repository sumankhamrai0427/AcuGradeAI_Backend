import uuid
from datetime import date, datetime

from flask import Blueprint, request, g

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

exam_bp = Blueprint("exam", __name__, url_prefix="/api/v1/exams")


def _resolve_student_for_request(session, payload: dict) -> Student:
    """A parent generates an exam on behalf of a named child; a student
    token (from /auth/child-login) generates it for themselves."""
    if g.current_user_role == "STUDENT":
        student = session.get(Student, g.current_user_id)
        if not student:
            raise NotFoundError("Student not found")
        return student

    require_fields(payload, ["studentId"])
    return assert_owns_student(session, payload["studentId"], g.current_user_id)


def _reset_daily_quota_if_new_day(student: Student):
    today = date.today()
    if student.last_exam_date != today:
        student.daily_exams_taken_today = 0


@exam_bp.post("/generate")
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

        # Quota is re-checked here server-side regardless of what the client
        # believes its remaining quota is (master prompt §27).
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


@exam_bp.post("/<exam_id>/submit")
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

        if g.current_user_role == "STUDENT" and exam.student_id != g.current_user_id:
            raise AppError("FORBIDDEN", "This exam does not belong to you", 403)
        elif g.current_user_role == "PARENT":
            assert_owns_student(session, exam.student_id, g.current_user_id)

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

        # Server-side XP/badges — the client can no longer compute or submit these.
        xp_earned = gamification_engine.compute_exam_xp(marks_obtained, time_taken_seconds)
        newly_unlocked_badges = gamification_engine.evaluate_badge_unlocks(
            session, student, marks_obtained, time_taken_seconds, exam.difficulty
        )
        gamification_engine.award_xp(session, student, xp_earned, f"exam:{exam.id}")

        # Rolling average + streak + mastery + misconceptions + learning path.
        updated_total = (student.total_exams_taken or 0) + 1
        student.average_score = round(
            ((float(student.average_score or 0) * (student.total_exams_taken or 0)) + marks_obtained) / updated_total, 2
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
