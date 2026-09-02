from datetime import date

from flask import g

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import User, Student, Exam, ExamSubmission, Runbook
from utils.constants import BOARDS, CLASS_GRADES
from utils.errors import NotFoundError
from utils.pagination import get_pagination_params, paginated_response
from utils.response import success
from utils.serializers import student_to_child_account


def statistics():
    """Public — matches the frontend's original unauthenticated GET /api/stats
    used by SuperAdminPanel's analytics tab and homepage counters."""
    with get_session() as session:
        total_generated = session.query(Exam).count()
        total_completed = session.query(ExamSubmission).count()
        total_runbooks = session.query(Runbook).filter(Runbook.status == "PUBLISHED").count()

        avg_row = session.query(ExamSubmission.accuracy_percentage).all()
        avg_score = (
            round(sum(float(r[0]) for r in avg_row) / len(avg_row) / 10, 2) if avg_row else 0
        )  # convert 0-100% back to an out-of-10 average, matching the frontend's displayed metric

        return success({
            "totalExamsGenerated": total_generated,
            "totalExamsCompleted": total_completed,
            "totalRunbooks": total_runbooks,
            "supportedBoards": BOARDS,
            "supportedGrades": CLASS_GRADES,
            "averagePlatformScore": avg_score,
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def admin_dashboard():
    with get_session() as session:
        return success({
            "totalUsers": session.query(User).count(),
            "totalStudents": session.query(Student).count(),
            "totalParents": session.query(User).filter(User.role == "PARENT").count(),
            "totalExamsToday": session.query(Exam).count(),  # refine with a date filter once volume warrants it
            "totalRunbooks": session.query(Runbook).count(),
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def list_users():
    page, limit, offset = get_pagination_params()
    with get_session() as session:
        total = session.query(User).count()
        users = session.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        items = [
            {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "status": u.status,
             "createdAt": u.created_at.isoformat()}
            for u in users
        ]
        return success(paginated_response(items, total, page, limit))


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def list_students():
    page, limit, offset = get_pagination_params()
    with get_session() as session:
        total = session.query(Student).count()
        students = session.query(Student).order_by(Student.created_at.desc()).offset(offset).limit(limit).all()
        items = [student_to_child_account(s) for s in students]
        return success(paginated_response(items, total, page, limit))


@token_required
@roles_required("ADMIN", "SUPER_ADMIN", "PARENT")
def reset_quota(student_id):
    with get_session() as session:
        student = session.get(Student, student_id)
        if not student:
            raise NotFoundError("Student not found")
        if g.current_user_role == "PARENT" and student.parent_id != g.current_user_id:
            raise NotFoundError("Student not found")
        student.daily_exams_taken_today = 0
        student.last_exam_date = date.today()
        return success({"reset": True})

