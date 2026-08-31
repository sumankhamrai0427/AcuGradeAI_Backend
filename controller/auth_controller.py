import hashlib
import uuid
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, g

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from model.models import User, Parent, RefreshToken, Student
from utils.config import config
from utils.errors import AppError, UnauthorizedError
from utils.response import success
from utils.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, verify_pin,
)
from utils.validators import require_fields, validate_email, validate_password_strength

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _issue_tokens(session, user: User) -> dict:
    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id, user.role)
    session.add(
        RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token_hash=_hash_token(refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    return {"accessToken": access_token, "refreshToken": refresh_token}


@auth_bp.post("/register")
def register():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["name", "email", "password"])
    validate_email(payload["email"])
    validate_password_strength(payload["password"])

    with get_session() as session:
        if session.query(User).filter(User.email == payload["email"]).first():
            raise AppError("EMAIL_TAKEN", "An account with this email already exists", 409)

        user = User(
            id=str(uuid.uuid4()), name=payload["name"], email=payload["email"],
            password_hash=hash_password(payload["password"]), role="PARENT", status="ACTIVE",
        )
        session.add(user)
        session.flush()
        session.add(Parent(id=user.id, subscription_tier="free"))
        session.flush()

        tokens = _issue_tokens(session, user)
        return success({"user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}, **tokens}, 201)


@auth_bp.post("/login")
def login():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["email", "password"])

    with get_session() as session:
        user = session.query(User).filter(User.email == payload["email"]).first()
        if not user or not verify_password(payload["password"], user.password_hash):
            raise UnauthorizedError("Invalid email or password", code="INVALID_CREDENTIALS")
        if user.status != "ACTIVE":
            raise UnauthorizedError("This account is not active", code="ACCOUNT_INACTIVE")

        tokens = _issue_tokens(session, user)
        return success({"user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}, **tokens})


@auth_bp.post("/child-login")
@token_required
def child_login():
    """A parent-authenticated request that mints a STUDENT-scoped token after
    verifying the child's PIN — mirrors the persona-switch + PIN field already
    present in the frontend's AddChildModal, now actually enforced."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["studentId", "pin"])

    with get_session() as session:
        student = session.get(Student, payload["studentId"])
        if not student or student.parent_id != g.current_user_id:
            raise AppError("NOT_FOUND", "Student not found", 404)
        if not verify_pin(payload["pin"], student.pin_hash):
            raise UnauthorizedError("Incorrect PIN", code="INVALID_PIN")

        access_token = create_access_token(student.id, "STUDENT")
        return success({"accessToken": access_token, "studentId": student.id})


@auth_bp.post("/refresh")
def refresh():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["refreshToken"])
    raw_token = payload["refreshToken"]

    try:
        decoded = decode_token(raw_token)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid or expired refresh token", code="TOKEN_INVALID")
    if decoded.get("type") != "refresh":
        raise UnauthorizedError("Not a refresh token")

    with get_session() as session:
        record = (
            session.query(RefreshToken)
            .filter(RefreshToken.token_hash == _hash_token(raw_token), RefreshToken.revoked.is_(False))
            .first()
        )
        if not record or record.expires_at < datetime.utcnow():
            raise UnauthorizedError("Refresh token expired or revoked", code="TOKEN_EXPIRED")

        user = session.get(User, decoded["sub"])
        if not user:
            raise UnauthorizedError("User no longer exists")

        record.revoked = True  # rotate refresh tokens on use
        tokens = _issue_tokens(session, user)
        return success(tokens)


@auth_bp.post("/logout")
@token_required
def logout():
    payload = request.get_json(force=True, silent=True) or {}
    raw_refresh = payload.get("refreshToken")
    if raw_refresh:
        with get_session() as session:
            record = session.query(RefreshToken).filter(RefreshToken.token_hash == _hash_token(raw_refresh)).first()
            if record:
                record.revoked = True
    return success({"loggedOut": True})
