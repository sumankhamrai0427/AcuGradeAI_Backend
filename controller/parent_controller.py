import json
import uuid

from flask import request, g
from sqlalchemy import text

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required, assert_owns_student
from model.models import Parent, Student, User, Role, ExamSubmission, LearningPathNode, StudentBadge
from utils.errors import AppError, NotFoundError
from utils.response import success
from utils.security import hash_pin, hash_password
from utils.serializers import student_to_child_account, submission_to_dict, learning_path_node_to_dict
from utils.validators import require_fields, validate_board, validate_class_grade, validate_pin


def get_child_registration_options():
    """Fetches active boards and class grades directly from DB via Stored Procedure."""
    with get_session() as session:
        result = session.execute(
            text("CALL sp_get_child_registration_masters()")
        ).mappings().first()

        boards_data = []
        grades_data = []
        if result:
            raw_boards = result.get("boards")
            raw_grades = result.get("class_grades")
            if raw_boards:
                boards_data = json.loads(raw_boards) if isinstance(raw_boards, str) else raw_boards
            if raw_grades:
                grades_data = json.loads(raw_grades) if isinstance(raw_grades, str) else raw_grades

        return success({
            "boards": boards_data,
            "classGrades": grades_data
        })


def _badge_ids_for(session, student_id: int) -> list[str]:
    return [
        sb.badge_id
        for sb in session.query(StudentBadge).filter(StudentBadge.student_id == student_id).all()
    ]


@token_required
@roles_required("PARENT")
def get_dashboard():
    """Consolidated Parent Dashboard API:
    Returns Parent Profile, Enriched Children (with Mastery & Recent Exams),
    Page Access (Menu Permissions), and Stats in ONE single round trip.
    """
    with get_session() as session:
        user = session.get(User, g.current_user_id)
        if not user:
            raise NotFoundError("User account not found")
        parent = session.get(Parent, g.current_user_id)
        if not parent:
            parent = Parent(id=user.id)
            session.add(parent)
            session.flush()

        from controller.auth_controller import get_page_access_for_role
        from helper.mastery_engine import get_topic_mastery_map

        # 1. Fetch children
        children_records = session.query(Student).filter(Student.parent_id == g.current_user_id).all()
        enriched_children = []
        all_recent_exams = []
        total_family_xp = 0

        for child in children_records:
            total_family_xp += (child.xp or 0)
            badge_ids = _badge_ids_for(session, child.id)
            child_dict = student_to_child_account(child, badge_ids)
            child_dict["topicMastery"] = get_topic_mastery_map(session, child.id)

            # Fetch recent exams for this child
            child_exams = (
                session.query(ExamSubmission)
                .filter(ExamSubmission.student_id == child.id)
                .order_by(ExamSubmission.submitted_at.desc())
                .limit(10)
                .all()
            )
            child_dict["recentExams"] = [submission_to_dict(s) for s in child_exams]
            all_recent_exams.extend(child_dict["recentExams"])
            enriched_children.append(child_dict)

        # Sort all exams descending by submission timestamp
        all_recent_exams.sort(key=lambda x: x.get("submittedAt") or "", reverse=True)

        # 2. Get Menu Permissions for PARENT role
        page_access = get_page_access_for_role(session, "PARENT")

        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": "parent",
            "createdAt": user.created_at.isoformat() if user.created_at else None,
        }

        return success({
            "profile": profile,
            "children": enriched_children,
            "recentExams": all_recent_exams,
            "pageAccess": page_access,
            "stats": {
                "totalChildren": len(enriched_children),
                "totalFamilyXP": total_family_xp,
            }
        })


@token_required
@roles_required("PARENT")
def get_me():
    with get_session() as session:
        user = session.get(User, g.current_user_id)
        if not user:
            raise NotFoundError("User account not found")
        parent = session.get(Parent, g.current_user_id)
        if not parent:
            parent = Parent(id=user.id)
            session.add(parent)
            session.flush()
        return success({
            "id": user.id, "name": user.name, "email": user.email, "role": "parent",
            "createdAt": user.created_at.isoformat() if user.created_at else None,
        })


@token_required
@roles_required("PARENT")
def list_children():
    with get_session() as session:
        children = session.query(Student).filter(Student.parent_id == g.current_user_id).all()
        return success([student_to_child_account(c, _badge_ids_for(session, c.id)) for c in children])


@token_required
@roles_required("PARENT")
def add_child():
    """Adds a child sub-account using Stored Procedure sp_add_child_account."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["name", "classGrade", "targetBoard"])
    
    password = str(payload.get("password") or payload.get("pin") or "1234").strip()
    if not password:
        raise AppError("VALIDATION_ERROR", "Password or PIN is required", 400)
    
    password_hash = hash_password(password)
    
    with get_session() as session:
        try:
            result = session.execute(
                text("""
                    CALL sp_add_child_account(
                        :parent_id,
                        :name,
                        :email,
                        :password_hash,
                        :class_grade,
                        :target_board,
                        :school_name,
                        :avatar
                    )
                """),
                {
                    "parent_id": g.current_user_id,
                    "name": payload["name"].strip(),
                    "email": payload.get("email", "").strip() or None,
                    "password_hash": password_hash,
                    "class_grade": payload["classGrade"].strip(),
                    "target_board": payload["targetBoard"].strip(),
                    "school_name": payload.get("schoolName", "").strip() or None,
                    "avatar": payload.get("avatar", "👦"),
                }
            ).mappings().first()
            session.commit()
        except Exception as e:
            if "CHILD_LIMIT_REACHED" in str(e):
                raise AppError("CHILD_LIMIT_REACHED", "Your subscription plan child limit has been reached", 403)
            raise
        
        if not result:
            raise AppError("CHILD_CREATION_FAILED", "Failed to create child account", 500)
        
        created_at_val = result.get("created_at")
        created_at_str = created_at_val.isoformat() if hasattr(created_at_val, "isoformat") else str(created_at_val)

        return success({
            "id": str(result["id"]),
            "name": result["name"],
            "email": result["email"],
            "parentId": str(result["parent_id"]),
            "avatar": result["avatar"],
            "classGrade": result["class_grade"],
            "targetBoard": result["target_board"],
            "schoolName": result["school_name"],
            "pin": password if len(password) == 4 and password.isdigit() else "••••",
            "dailyExamsTakenToday": result["daily_exams_taken_today"],
            "totalExamsTaken": result["total_exams_taken"],
            "averageScore": float(result["average_score"] or 0),
            "streakDays": result["streak_days"],
            "xp": result["xp"],
            "level": result["level"],
            "badges": [],
            "topicMastery": {},
            "createdAt": created_at_str,
        }, 201)


@token_required
@roles_required("PARENT")
def update_child(student_id):
    payload = request.get_json(force=True, silent=True) or {}
    s_id = int(student_id) if str(student_id).isdigit() else student_id

    with get_session() as session:
        student = assert_owns_student(session, s_id, g.current_user_id)

        if "name" in payload and student.user:
            student.user.name = payload["name"]
        for field, attr in [
            ("avatar", "avatar"), ("classGrade", "class_grade"), ("targetBoard", "target_board"),
            ("schoolName", "school_name"),
        ]:
            if field in payload:
                setattr(student, attr, payload[field])
        if payload.get("pin"):
            validate_pin(payload["pin"])
            student.pin_hash = hash_pin(payload["pin"])

        return success(student_to_child_account(student, _badge_ids_for(session, student.id)))


@token_required
@roles_required("PARENT")
def delete_child(student_id):
    s_id = int(student_id) if str(student_id).isdigit() else student_id
    with get_session() as session:
        student = assert_owns_student(session, s_id, g.current_user_id)
        user = session.get(User, student.id)
        session.delete(student)
        if user:
            session.delete(user)
        return success({"deleted": True})


@token_required
@roles_required("PARENT")
def child_overview(student_id):
    s_id = int(student_id) if str(student_id).isdigit() else student_id
    with get_session() as session:
        student = assert_owns_student(session, s_id, g.current_user_id)
        recent_submissions = (
            session.query(ExamSubmission)
            .filter(ExamSubmission.student_id == s_id)
            .order_by(ExamSubmission.submitted_at.desc())
            .limit(10)
            .all()
        )
        from helper.mastery_engine import get_topic_mastery_map

        return success({
            "child": student_to_child_account(student, _badge_ids_for(session, student.id)),
            "recentExams": [submission_to_dict(s) for s in recent_submissions],
            "topicMastery": get_topic_mastery_map(session, s_id),
        })


@token_required
@roles_required("PARENT")
def child_learning_path(student_id):
    s_id = int(student_id) if str(student_id).isdigit() else student_id
    with get_session() as session:
        assert_owns_student(session, s_id, g.current_user_id)
        nodes = session.query(LearningPathNode).filter(LearningPathNode.student_id == s_id).all()
        return success([learning_path_node_to_dict(n) for n in nodes])
