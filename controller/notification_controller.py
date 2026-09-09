import uuid
from datetime import datetime
from flask import g, request

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from model.models import Notification, User
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
        created_at=datetime.utcnow(),
    )
    session.add(notif)
    session.flush()
    return notif


def notification_to_dict(notif: Notification) -> dict:
    return {
        "id": notif.id,
        "userId": notif.user_id,
        "senderId": notif.sender_id,
        "type": notif.type,
        "title": notif.title,
        "message": notif.message,
        "actionUrl": notif.action_url,
        "metadata": notif.metadata_json or {},
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

        return success({
            "notifications": [notification_to_dict(n) for n in notifs],
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
