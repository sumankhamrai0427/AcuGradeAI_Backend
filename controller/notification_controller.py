from utils.date_helper import now_ist
import uuid
from datetime import datetime
from flask import g, request

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from model.models import Notification, User, ScheduledExam
from utils.errors import NotFoundError
from utils.response import success


def create_notification(
    session,
    user_id: int,
    sender_id: int | None,
    notif_type: str,
    title: str,
    message: str,
    action_url: str | None = None,
    metadata_json: dict | None = None,
) -> Notification:
    """Helper to insert a notification into the DB."""
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        sender_id=sender_id,
        type=notif_type,
        title=title,
        message=message,
        action_url=action_url,
        metadata_json=metadata_json,
        is_read=False,
        created_at=now_ist(),
    )
    session.add(notif)
    session.flush()
    return notif


def notification_to_dict(notif: Notification, status_map: dict | None = None) -> dict:
    meta = dict(notif.metadata_json or {})
    seid = meta.get("scheduledExamId")
    
    if status_map and seid in status_map:
        meta["status"] = status_map[seid]["status"]
        if status_map[seid].get("submissionId"):
            meta["submissionId"] = status_map[seid]["submissionId"]
        if status_map[seid].get("examId"):
            meta["examId"] = status_map[seid]["examId"]
    elif not meta.get("status"):
        if notif.type in ("SCHEDULED_EXAM_COMPLETED", "EXAM_SUBMITTED"):
            meta["status"] = "SUBMITTED"
        elif notif.type == "EXAM_ASSIGNED":
            meta["status"] = "PENDING"

    return {
        "id": notif.id,
        "userId": notif.user_id,
        "senderId": notif.sender_id,
        "type": notif.type,
        "title": notif.title,
        "message": notif.message,
        "actionUrl": notif.action_url,
        "metadata": meta,
        "isRead": bool(notif.is_read),
        "createdAt": notif.created_at.isoformat() if notif.created_at else None,
    }


@token_required
def get_notifications():
    """Returns recent notifications and unread count for current user."""
    user_id = g.current_user_id
    with get_session() as session:
        notifs = (
            session.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        unread_count = (
            session.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

        # Batch lookup scheduled exams to enrich live status
        scheduled_exam_ids = []
        for n in notifs:
            if n.metadata_json and isinstance(n.metadata_json, dict):
                seid = n.metadata_json.get("scheduledExamId")
                if seid:
                    scheduled_exam_ids.append(seid)

        status_map = {}
        if scheduled_exam_ids:
            sched_records = (
                session.query(ScheduledExam)
                .filter(ScheduledExam.id.in_(scheduled_exam_ids))
                .all()
            )
            for s in sched_records:
                status_map[s.id] = {
                    "status": s.status or "PENDING",
                    "submissionId": str(s.submission_id) if s.submission_id else None,
                    "examId": str(s.exam_id) if s.exam_id else None,
                }

        return success({
            "notifications": [notification_to_dict(n, status_map) for n in notifs],
            "unreadCount": unread_count,
        })


@token_required
def mark_as_read(notification_id: str):
    """Mark a single notification as read."""
    user_id = g.current_user_id
    with get_session() as session:
        notif = session.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if not notif:
            raise NotFoundError("Notification not found")

        notif.is_read = True
        session.flush()

        unread_count = (
            session.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )
        return success({
            "notification": notification_to_dict(notif),
            "unreadCount": unread_count,
        })


@token_required
def mark_all_as_read():
    """Mark all notifications as read for the logged in user."""
    user_id = g.current_user_id
    with get_session() as session:
        session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True}, synchronize_session=False)

        return success({"unreadCount": 0})
