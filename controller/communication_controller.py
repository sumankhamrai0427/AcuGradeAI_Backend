import secrets
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, request, g

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required, assert_owns_student
from model.models import Teacher, Conversation, Message, SharedDossier, ExamSubmission
from utils.errors import NotFoundError, ValidationError
from utils.response import success
from utils.validators import require_fields

communication_bp = Blueprint("communication", __name__, url_prefix="/api/v1")


def _teacher_to_dict(teacher: Teacher) -> dict:
    user = getattr(teacher, "user", None)
    return {
        "id": teacher.id,
        "name": user.name if user else "",
        "role": teacher.role_title,
        "subject": teacher.subject,
        "schoolName": teacher.school_name,
        "email": user.email if user else "",
        "phone": teacher.phone,
        "verified": bool(teacher.verified),
    }


def _message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "conversationId": message.conversation_id,
        "senderRole": message.sender_role,
        "senderId": message.sender_id,
        "message": message.message,
        "timestamp": message.created_at.isoformat(),
        "attachedSubmissionId": message.attached_submission_id,
        "actionItems": message.action_items or [],
        "status": message.status,
    }


def _dossier_to_dict(d: SharedDossier) -> dict:
    return {
        "id": d.id,
        "studentId": d.student_id,
        "shareToken": d.share_token,
        "createdAt": d.created_at.isoformat(),
        "expiresAt": d.expires_at.isoformat(),
        "notes": d.notes,
        "recipients": d.recipients,
        "includedSubmissionsCount": d.included_submissions_count,
        "status": d.status,
    }


@communication_bp.get("/teachers")
@token_required
def list_teachers():
    with get_session() as session:
        teachers = session.query(Teacher).all()
        return success([_teacher_to_dict(t) for t in teachers])


@communication_bp.get("/conversations")
@token_required
@roles_required("PARENT")
def list_conversations():
    with get_session() as session:
        conversations = session.query(Conversation).filter(Conversation.parent_id == g.current_user_id).all()
        return success([
            {
                "id": c.id, "teacherId": c.teacher_id, "studentId": c.student_id,
                "createdAt": c.created_at.isoformat(),
                "messages": [_message_to_dict(m) for m in c.messages],
            }
            for c in conversations
        ])


@communication_bp.get("/conversations/<conversation_id>")
@token_required
def get_conversation(conversation_id):
    with get_session() as session:
        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            raise NotFoundError("Conversation not found")
        if g.current_user_role == "PARENT" and conversation.parent_id != g.current_user_id:
            raise NotFoundError("Conversation not found")
        if g.current_user_role == "TEACHER" and conversation.teacher_id != g.current_user_id:
            raise NotFoundError("Conversation not found")
        return success([_message_to_dict(m) for m in conversation.messages])


@communication_bp.post("/conversations")
@token_required
@roles_required("PARENT")
def create_or_get_conversation():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["teacherId", "studentId"])

    with get_session() as session:
        assert_owns_student(session, payload["studentId"], g.current_user_id)
        teacher = session.get(Teacher, payload["teacherId"])
        if not teacher:
            raise NotFoundError("Teacher not found")

        conversation = (
            session.query(Conversation)
            .filter(
                Conversation.parent_id == g.current_user_id,
                Conversation.teacher_id == payload["teacherId"],
                Conversation.student_id == payload["studentId"],
            )
            .one_or_none()
        )
        if not conversation:
            conversation = Conversation(
                id=str(uuid.uuid4()), parent_id=g.current_user_id,
                teacher_id=payload["teacherId"], student_id=payload["studentId"],
            )
            session.add(conversation)
            session.flush()
        return success({"id": conversation.id}, 201)


@communication_bp.post("/conversations/<conversation_id>/messages")
@token_required
def send_message(conversation_id):
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["message"])

    with get_session() as session:
        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            raise NotFoundError("Conversation not found")

        if g.current_user_role == "PARENT":
            if conversation.parent_id != g.current_user_id:
                raise NotFoundError("Conversation not found")
            sender_role = "parent"
        elif g.current_user_role == "TEACHER":
            if conversation.teacher_id != g.current_user_id:
                raise NotFoundError("Conversation not found")
            sender_role = "teacher"
        else:
            raise ValidationError("Only parents or teachers may send messages")

        message = Message(
            id=str(uuid.uuid4()), conversation_id=conversation_id, sender_role=sender_role,
            sender_id=g.current_user_id, message=payload["message"],
            attached_submission_id=payload.get("attachedSubmissionId"),
            action_items=payload.get("actionItems"), status="sent",
        )
        session.add(message)
        session.flush()
        return success(_message_to_dict(message), 201)


@communication_bp.put("/messages/<message_id>/read")
@token_required
def mark_message_read(message_id):
    with get_session() as session:
        message = session.get(Message, message_id)
        if not message:
            raise NotFoundError("Message not found")
        message.status = "read"
        return success(_message_to_dict(message))


@communication_bp.post("/dossiers")
@token_required
@roles_required("PARENT")
def create_dossier():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["studentId", "recipients"])

    with get_session() as session:
        student = assert_owns_student(session, payload["studentId"], g.current_user_id)
        submissions_count = session.query(ExamSubmission).filter(ExamSubmission.student_id == student.id).count()

        dossier = SharedDossier(
            id=str(uuid.uuid4()), student_id=student.id, parent_id=g.current_user_id,
            share_token=f"ACU-SHARE-{secrets.token_hex(4).upper()}",  # server-generated, not client Math.random()
            notes=payload.get("notes", ""), recipients=payload["recipients"],
            included_submissions_count=submissions_count, status="active",
            created_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(days=30),
        )
        session.add(dossier)
        session.flush()
        return success(_dossier_to_dict(dossier), 201)


@communication_bp.get("/dossiers")
@token_required
@roles_required("PARENT")
def list_dossiers():
    with get_session() as session:
        dossiers = session.query(SharedDossier).filter(SharedDossier.parent_id == g.current_user_id).all()
        return success([_dossier_to_dict(d) for d in dossiers])
