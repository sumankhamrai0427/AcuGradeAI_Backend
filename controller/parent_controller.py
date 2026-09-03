import uuid

from flask import request, g

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required, assert_owns_student
from model.models import Parent, Student, User, Role, ExamSubmission, LearningPathNode, StudentBadge, SubscriptionPlan
from utils.errors import AppError, NotFoundError
from utils.response import success
from utils.security import hash_pin
from utils.serializers import student_to_child_account, submission_to_dict, learning_path_node_to_dict
from utils.validators import require_fields, validate_board, validate_class_grade, validate_pin



def _badge_ids_for(session, student_id) -> list[str]:
    s_id = int(student_id) if str(student_id).isdigit() else student_id
    rows = session.query(StudentBadge).filter(StudentBadge.student_id == s_id).all()
    return [r.badge_id for r in rows]


@token_required
@roles_required("PARENT")
def get_dashboard():
    """Consolidated Parent Dashboard API:
    Returns Parent Profile, Subscription, Enriched Children (with Mastery & Recent Exams),
    Page Access (Menu Permissions), and Stats in ONE single round trip.
    """
    with get_session() as session:
        user = session.get(User, g.current_user_id)
        if not user:
            raise NotFoundError("User account not found")
        parent = session.get(Parent, g.current_user_id)
        if not parent:
            parent = Parent(id=user.id, subscription_tier="free")
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
            "subscriptionTier": parent.subscription_tier,
            "subscriptionExpiry": parent.subscription_expiry.isoformat() if parent.subscription_expiry else None,
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
            parent = Parent(id=user.id, subscription_tier="free")
            session.add(parent)
            session.flush()
        return success({
            "id": user.id, "name": user.name, "email": user.email, "role": "parent",
            "subscriptionTier": parent.subscription_tier,
            "subscriptionExpiry": parent.subscription_expiry.isoformat() if parent.subscription_expiry else None,
            "createdAt": user.created_at.isoformat(),
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
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["name", "classGrade", "targetBoard", "pin"])
    validate_class_grade(payload["classGrade"])
    validate_board(payload["targetBoard"])
    validate_pin(payload["pin"])

    with get_session() as session:
        parent = session.get(Parent, g.current_user_id)
        plan = session.get(SubscriptionPlan, parent.subscription_tier)
        current_count = session.query(Student).filter(Student.parent_id == parent.id).count()
        if plan and plan.max_children != "unlimited" and current_count >= int(plan.max_children):
            raise AppError(
                "CHILD_LIMIT_REACHED",
                f"Your {parent.subscription_tier} plan allows up to {plan.max_children} children",
                403,
            )

        role_record = session.query(Role).filter(Role.role_name == "STUDENT").first()
        student_role_id = role_record.id if role_record else 1

        user = User(
            name=payload["name"],
            email=f"child+{uuid.uuid4()}@acugrade.local",
            password_hash=hash_pin(payload["pin"]),
            role_id=student_role_id,
            is_active=True,
        )
        session.add(user)
        session.flush()

        student = Student(
            id=user.id,
            parent_id=parent.id,
            avatar=payload.get("avatar", "🧑‍🎓"),
            class_grade=payload["classGrade"],
            target_board=payload["targetBoard"],
            school_name=payload.get("schoolName"),
            pin_hash=hash_pin(payload["pin"]),
            xp=250,
            level=1,
        )
        session.add(student)
        session.flush()
        return success(student_to_child_account(student, []), 201)


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
