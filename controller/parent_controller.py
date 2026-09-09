import json
import uuid

from flask import request, g
from sqlalchemy import text, func

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required, assert_owns_student
from datetime import datetime
from model.models import Parent, Student, User, Role, ExamSubmission, LearningPathNode, StudentBadge, ScheduledExam
from utils.errors import AppError, NotFoundError
from utils.response import success
from utils.audit_helper import log_audit
from utils.security import hash_pin, hash_password
from utils.serializers import student_to_child_account, submission_to_dict, learning_path_node_to_dict
from utils.constants import BOARD_CLASS_MAPPING
from utils.validators import require_fields, validate_board, validate_class_grade, validate_board_class, validate_pin, validate_username


def get_child_registration_options():
    """Fetches active boards and class grades directly from DB via Stored Procedure."""
    with get_session() as session:
        result = session.execute(
            text("CALL sp_get_child_registration_masters()")
        ).mappings().first()

        boards_data = []
        classes_data = []
        if result:
            raw_boards = result.get("boards")
            raw_classes = result.get("classes") or result.get("class_grades")
            if raw_boards:
                parsed_boards = json.loads(raw_boards) if isinstance(raw_boards, str) else raw_boards
                boards_data = [{"id": b["id"], "name": b["name"], "description": b.get("description", "")} for b in parsed_boards if isinstance(b, dict) and "id" in b and "name" in b]
            if raw_classes:
                parsed_classes = json.loads(raw_classes) if isinstance(raw_classes, str) else raw_classes
                classes_data = [{"id": c["id"], "name": c["name"]} for c in parsed_classes if isinstance(c, dict) and "id" in c and "name" in c]

        return success({
            "boards": boards_data,
            "classes": classes_data,
            "classGrades": classes_data,
            "boardClassesMap": BOARD_CLASS_MAPPING,
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
    """Adds a child sub-account with unique username, parent's email, and initial student profile."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["name", "username", "classGrade", "targetBoard"])
    
    username = payload["username"].strip()
    validate_username(username)

    password = str(payload.get("password") or payload.get("pin") or "1234").strip()
    if not password:
        raise AppError("VALIDATION_ERROR", "Password is required", 400)
    
    password_hash = hash_password(password)
    name = payload["name"].strip()
    class_grade = payload["classGrade"].strip()
    target_board = payload["targetBoard"].strip()
    validate_board_class(target_board, class_grade)
    school_name = payload.get("schoolName", "").strip() or None
    avatar = payload.get("avatar", "👦")
    
    with get_session() as session:
        # 1. Check global username uniqueness (case-insensitive)
        existing_user = session.query(User).filter(func.lower(User.username) == func.lower(username)).first()
        if existing_user:
            raise AppError("USERNAME_TAKEN", f"The username '{username}' is already taken. Please choose another username.", 409)

        # 2. Get parent user to assign parent's email to child
        parent_user = session.get(User, g.current_user_id)
        parent_email = parent_user.email if parent_user else None

        # 3. Get STUDENT role
        student_role = session.query(Role).filter(Role.role_name == "STUDENT").first()
        if not student_role:
            student_role = session.query(Role).filter(Role.id == 1).first()
        if not student_role:
            student_role = Role(role_name="STUDENT", is_active=True)
            session.add(student_role)
            session.flush()

        # 4. Create User for child
        child_user = User(
            name=name,
            username=username,
            email=parent_email,
            password_hash=password_hash,
            role_id=student_role.id,
            is_active=True,
            created_by=g.current_user_id,
        )
        session.add(child_user)
        session.flush()

        # 5. Create Student record
        student = Student(
            id=child_user.id,
            parent_id=g.current_user_id,
            avatar=avatar,
            class_grade=class_grade,
            target_board=target_board,
            school_name=school_name,
            pin_hash=hash_pin(password[:4] if len(password) >= 4 and password[:4].isdigit() else "1234"),
            xp=0,
            level=1,
            streak_days=0,
            total_exams_taken=0,
            average_score=0.0,
            daily_exams_taken_today=0,
        )
        session.add(student)
        log_audit(
            session,
            action="CHILD_CREATED",
            user_id=g.current_user_id,
            entity_type="STUDENT_PROFILE",
            entity_id=str(student.id),
            request=request,
        )
        session.commit()

        return success(student_to_child_account(student, []), 201)


@token_required
@roles_required("PARENT")
def update_child(student_id):
    payload = request.get_json(force=True, silent=True) or {}
    s_id = int(student_id) if str(student_id).isdigit() else student_id

    with get_session() as session:
        student = assert_owns_student(session, s_id, g.current_user_id)

        new_class = payload.get("classGrade", student.class_grade)
        new_board = payload.get("targetBoard", student.target_board)
        if "classGrade" in payload or "targetBoard" in payload:
            validate_board_class(new_board, new_class)

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

        log_audit(
            session,
            action="CHILD_UPDATED",
            user_id=g.current_user_id,
            entity_type="STUDENT_PROFILE",
            entity_id=str(student.id),
            request=request,
        )
        session.commit()

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
        log_audit(
            session,
            action="CHILD_DELETED",
            user_id=g.current_user_id,
            entity_type="STUDENT_PROFILE",
            entity_id=str(s_id),
            request=request,
        )
        session.commit()
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


def scheduled_exam_to_dict(se: ScheduledExam) -> dict:
    return {
        "id": se.id,
        "parentId": se.parent_id,
        "studentId": se.student_id,
        "studentName": se.student.user.name if se.student and se.student.user else "Student",
        "studentAvatar": se.student.avatar if se.student else "🧑‍🎓",
        "title": se.title,
        "subject": se.subject,
        "chapterTopic": se.chapter_topic,
        "board": se.board,
        "classGrade": se.class_grade,
        "difficulty": se.difficulty,
        "questionCount": se.question_count,
        "timeLimitMinutes": se.time_limit_minutes,
        "scheduledAt": se.scheduled_at.isoformat() if se.scheduled_at else None,
        "dueDate": se.due_date.isoformat() if se.due_date else None,
        "parentInstructions": se.parent_instructions,
        "status": se.status,
        "examId": se.exam_id,
        "submissionId": se.submission_id,
        "score": se.submission.marks_obtained if se.submission else None,
        "totalMarks": se.submission.total_marks if se.submission else None,
        "accuracy": float(se.submission.accuracy_percentage) if se.submission and se.submission.accuracy_percentage is not None else None,
        "createdAt": se.created_at.isoformat() if se.created_at else None,
    }


@token_required
@roles_required("PARENT")
def schedule_exam():
    """Parent schedules a customized exam for their child."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["studentId", "subject"])

    student_id = int(payload["studentId"])
    from utils.constants import normalize_subject
    from utils.validators import validate_subject
    subject = normalize_subject(str(payload["subject"]).strip())
    validate_subject(subject)
    chapter_topic = str(payload.get("chapterTopic", "")).strip() or None
    difficulty = str(payload.get("difficulty", "medium")).lower()
    if difficulty not in ["simple", "medium", "hard"]:
        difficulty = "medium"
    question_count = max(5, min(25, int(payload.get("questionCount", 10))))
    time_limit_minutes = max(5, min(60, int(payload.get("timeLimitMinutes", 15))))
    parent_instructions = str(payload.get("parentInstructions", "")).strip() or None

    scheduled_at_str = payload.get("scheduledAt")
    due_date_str = payload.get("dueDate")

    scheduled_at = None
    due_date = None
    if scheduled_at_str:
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
        except Exception:
            pass
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except Exception:
            pass

    with get_session() as session:
        student = assert_owns_student(session, student_id, g.current_user_id)
        student_name = student.user.name if student.user else "Student"

        title = payload.get("title") or f"{student_name}'s {subject} Assessment ({question_count} Questions)"

        scheduled_exam = ScheduledExam(
            id=str(uuid.uuid4()),
            parent_id=g.current_user_id,
            student_id=student.id,
            title=title,
            subject=subject,
            chapter_topic=chapter_topic,
            board=student.target_board,
            class_grade=student.class_grade,
            difficulty=difficulty,
            question_count=question_count,
            time_limit_minutes=time_limit_minutes,
            scheduled_at=scheduled_at,
            due_date=due_date,
            parent_instructions=parent_instructions,
            status="PENDING",
            created_at=datetime.utcnow(),
        )
        session.add(scheduled_exam)
        session.flush()

        # Send Real-Time Notification to Student
        from controller.notification_controller import create_notification
        create_notification(
            session=session,
            user_id=student.id,
            sender_id=g.current_user_id,
            notif_type="EXAM_ASSIGNED",
            title=f"New Exam Assigned by Parent 📝",
            message=f"Your parent scheduled an exam on '{subject}{' - ' + chapter_topic if chapter_topic else ''}' ({question_count} Marks, {difficulty.capitalize()}).",
            action_url="/arena",
            metadata_json={
                "scheduledExamId": scheduled_exam.id,
                "subject": subject,
                "chapterTopic": chapter_topic,
                "difficulty": difficulty,
                "questionCount": question_count,
            }
        )

        log_audit(
            session,
            action="EXAM_SCHEDULED_BY_PARENT",
            user_id=g.current_user_id,
            entity_type="SCHEDULED_EXAM",
            entity_id=str(scheduled_exam.id),
            request=request,
        )
        session.commit()

        return success(
            {"scheduledExam": scheduled_exam_to_dict(scheduled_exam)},
            201
        )


@token_required
@roles_required("PARENT")
def list_scheduled_exams():
    """List all scheduled exams created by the parent."""
    with get_session() as session:
        exams = (
            session.query(ScheduledExam)
            .filter(ScheduledExam.parent_id == g.current_user_id)
            .order_by(ScheduledExam.created_at.desc())
            .all()
        )
        return success({"scheduledExams": [scheduled_exam_to_dict(se) for se in exams]})


@token_required
@roles_required("PARENT")
def delete_scheduled_exam(scheduled_exam_id: str):
    """Delete or cancel a scheduled exam."""
    with get_session() as session:
        se = session.query(ScheduledExam).filter(
            ScheduledExam.id == scheduled_exam_id,
            ScheduledExam.parent_id == g.current_user_id
        ).first()
        if not se:
            raise NotFoundError("Scheduled exam not found")

        session.delete(se)
        session.commit()
        return success({"deleted": True})

