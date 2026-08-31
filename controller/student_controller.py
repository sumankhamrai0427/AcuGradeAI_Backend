from flask import Blueprint, g

from database.dbConnection import get_session
from helper.mastery_engine import get_topic_mastery_map
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import Student, ExamSubmission, LearningPathNode, StudentBadge
from utils.errors import NotFoundError
from utils.response import success
from utils.serializers import student_to_child_account, submission_to_dict, learning_path_node_to_dict

student_bp = Blueprint("student", __name__, url_prefix="/api/v1/students")


@student_bp.get("/me")
@token_required
@roles_required("STUDENT")
def get_me():
    with get_session() as session:
        student = session.get(Student, g.current_user_id)
        if not student:
            raise NotFoundError("Student not found")
        badge_ids = [r.badge_id for r in session.query(StudentBadge).filter(StudentBadge.student_id == student.id).all()]
        return success(student_to_child_account(student, badge_ids))


@student_bp.get("/me/overview")
@token_required
@roles_required("STUDENT")
def my_overview():
    with get_session() as session:
        student = session.get(Student, g.current_user_id)
        if not student:
            raise NotFoundError("Student not found")
        recent = (
            session.query(ExamSubmission)
            .filter(ExamSubmission.student_id == student.id)
            .order_by(ExamSubmission.submitted_at.desc())
            .limit(10)
            .all()
        )
        return success({
            "child": student_to_child_account(student),
            "recentExams": [submission_to_dict(s) for s in recent],
            "topicMastery": get_topic_mastery_map(session, student.id),
        })


@student_bp.get("/me/learning-path")
@token_required
@roles_required("STUDENT")
def my_learning_path():
    with get_session() as session:
        nodes = session.query(LearningPathNode).filter(LearningPathNode.student_id == g.current_user_id).all()
        return success([learning_path_node_to_dict(n) for n in nodes])
