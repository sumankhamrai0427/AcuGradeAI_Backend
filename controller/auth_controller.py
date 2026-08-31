import hashlib
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, g
from sqlalchemy import text

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
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


def _issue_tokens(session, user_id: int, role_name: str) -> dict:
    normalized_role = str(role_name).strip().upper()
    access_token = create_access_token(user_id, normalized_role)
    refresh_token = create_refresh_token(user_id, normalized_role)
    expires_at = datetime.utcnow() + timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    session.execute(
        text("CALL sp_save_refresh_token(:user_id, :token_hash, :expires_at)"),
        {
            "user_id": user_id,
            "token_hash": _hash_token(refresh_token),
            "expires_at": expires_at,
        }
    )
    return {"accessToken": access_token, "refreshToken": refresh_token}


def _get_page_access(session, role_name: str) -> list[dict]:
    rows = session.execute(
        text("CALL sp_get_role_menu_permissions(:role_name)"),
        {"role_name": role_name}
    ).mappings().all()

    return [
        {
            "id": r["id"],
            "pageName": r["page_name"],
            "pageRoute": r["page_route"],
            "icon": r["icon"],
            "menuOrder": r["menu_order"],
            "isActive": r["is_active"],
        }
        for r in rows
    ]


@auth_bp.post("/register")
def register():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["name", "email", "password"])
    validate_email(payload["email"])
    validate_password_strength(payload["password"])

    password_hash = hash_password(payload["password"])
    requested_role = str(payload.get("role", "PARENT")).strip().upper()
    role_name = "TEACHER" if requested_role == "TEACHER" else "PARENT"

    with get_session() as session:
        try:
            result = session.execute(
                text("CALL sp_register_parent(:name, :email, :password_hash, :role_name)"),
                {
                    "name": payload["name"].strip(),
                    "email": payload["email"].strip().lower(),
                    "password_hash": password_hash,
                    "role_name": role_name,
                }
            ).mappings().first()
            session.commit()
        except Exception as e:
            if "EMAIL_TAKEN" in str(e):
                raise AppError("EMAIL_TAKEN", "An account with this email already exists", 409)
            raise

        if not result:
            raise AppError("REGISTRATION_FAILED", "Failed to register user", 500)

        tokens = _issue_tokens(session, result["id"], result["role_name"])
        page_access = _get_page_access(session, result["role_name"])
        session.commit()

        created_at_val = result.get("created_at")
        created_at_str = created_at_val.isoformat() if hasattr(created_at_val, "isoformat") else str(created_at_val)

        return success(
            {
                "tokens": {
                    "accessToken": tokens["accessToken"],
                    "refreshToken": tokens["refreshToken"],
                    "tokenType": "Bearer",
                    "expiresIn": config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                },
                "accessToken": tokens["accessToken"],
                "refreshToken": tokens["refreshToken"],
                "user": {
                    "id": result["id"],
                    "name": result["name"],
                    "email": result["email"],
                    "roleId": result["role_id"],
                    "roleName": result["role_name"],
                    "role": result["role_name"],
                    "subscriptionTier": result.get("subscription_tier", "free"),
                    "isActive": result["is_active"],
                    "createdAt": created_at_str,
                },
                "pageAccess": page_access,
            },
            status_code=201,
            message="User registered successfully",
        )


@auth_bp.post("/login")
def login():
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["email", "password"])

    email = payload["email"].strip()

    with get_session() as session:
        user = session.execute(
            text("CALL sp_get_user_for_login(:email)"),
            {"email": email}
        ).mappings().first()

        if not user or not verify_password(payload["password"], user["password_hash"]):
            raise UnauthorizedError("Invalid email or password", code="INVALID_CREDENTIALS")
        if not user["is_active"]:
            raise UnauthorizedError("This account is not active", code="ACCOUNT_INACTIVE")

        tokens = _issue_tokens(session, user["id"], user["role_name"])
        page_access = _get_page_access(session, user["role_name"])
        session.commit()

        return success(
            {
                "tokens": {
                    "accessToken": tokens["accessToken"],
                    "refreshToken": tokens["refreshToken"],
                    "tokenType": "Bearer",
                    "expiresIn": config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                },
                "accessToken": tokens["accessToken"],
                "refreshToken": tokens["refreshToken"],
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "roleId": user["role_id"],
                    "roleName": user["role_name"],
                    "role": user["role_name"],
                    "subscriptionTier": user.get("subscription_tier", "free"),
                    "isActive": user["is_active"],
                },
                "pageAccess": page_access,
            },
            status_code=200,
            message="Login successful",
        )


@auth_bp.get("/verify")
@token_required
def verify_session():
    """Validates the current session token with the database using Stored Procedure."""
    user_id = g.current_user_id

    with get_session() as session:
        user = session.execute(
            text("CALL sp_verify_user_session(:user_id)"),
            {"user_id": user_id}
        ).mappings().first()

        if not user or not user["is_active"]:
            raise UnauthorizedError("Session invalid or account inactive", code="SESSION_INVALID")

        page_access = _get_page_access(session, user["role_name"])

        return success(
            {
                "valid": True,
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "roleId": user["role_id"],
                    "roleName": user["role_name"],
                    "role": user["role_name"],
                    "isActive": user["is_active"],
                },
                "pageAccess": page_access,
            },
            status_code=200,
            message="Session verified successfully",
        )


@auth_bp.get("/menu-permissions")
@token_required
def get_menu_permissions():
    """Returns dynamic page access & navigation permissions for the active role."""
    role_name = g.current_user_role

    with get_session() as session:
        page_access = _get_page_access(session, role_name)
        return success(
            {"role": role_name, "menuItems": page_access, "pageAccess": page_access},
            status_code=200,
            message="Menu permissions retrieved successfully",
        )


@auth_bp.get("/roles")
def get_registration_roles():
    """Public endpoint to fetch active roles available for self-registration."""
    with get_session() as session:
        rows = session.execute(text("CALL sp_get_registration_roles()")).mappings().all()
        roles_list = [
            {
                "id": r["id"],
                "roleName": r["role_name"],
                "displayName": r["display_name"],
                "description": r["description"],
                "icon": r["icon"],
                "isActive": r["is_active"],
            }
            for r in rows
        ]
        return success(
            roles_list,
            status_code=200,
            message="Registration roles retrieved successfully",
        )



@auth_bp.post("/child-login")
@token_required
def child_login():
    """Verifies child PIN using Stored Procedure and mints a STUDENT-scoped JWT token."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["studentId", "pin"])

    parent_id = g.current_user_id
    student_id = int(payload["studentId"])

    with get_session() as session:
        student = session.execute(
            text("CALL sp_get_child_for_login(:student_id, :parent_id)"),
            {"student_id": student_id, "parent_id": parent_id}
        ).mappings().first()

        if not student:
            raise AppError("NOT_FOUND", "Student not found or access denied", 404)
        if not verify_pin(payload["pin"], student["pin_hash"]):
            raise UnauthorizedError("Incorrect PIN", code="INVALID_PIN")

        access_token = create_access_token(student["id"], "STUDENT")
        page_access = _get_page_access(session, "STUDENT")

        return success(
            {
                "tokens": {
                    "accessToken": access_token,
                    "tokenType": "Bearer",
                    "expiresIn": config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                },
                "accessToken": access_token,
                "studentId": student["id"],
                "pageAccess": page_access,
            },
            status_code=200,
            message="Child authenticated successfully",
        )


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

    token_hash = _hash_token(raw_token)

    with get_session() as session:
        try:
            user = session.execute(
                text("CALL sp_validate_and_rotate_refresh_token(:token_hash)"),
                {"token_hash": token_hash}
            ).mappings().first()
            session.commit()
        except Exception:
            raise UnauthorizedError("Refresh token expired or revoked", code="TOKEN_EXPIRED")

        if not user or not user["is_active"]:
            raise UnauthorizedError("User no longer exists or is inactive")

        tokens = _issue_tokens(session, user["id"], user["role_name"])
        page_access = _get_page_access(session, user["role_name"])
        session.commit()

        return success(
            {
                "tokens": {
                    "accessToken": tokens["accessToken"],
                    "refreshToken": tokens["refreshToken"],
                    "tokenType": "Bearer",
                    "expiresIn": config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                },
                "accessToken": tokens["accessToken"],
                "refreshToken": tokens["refreshToken"],
                "pageAccess": page_access,
            },
            status_code=200,
            message="Token refreshed successfully",
        )


@auth_bp.post("/logout")
@token_required
def logout():
    payload = request.get_json(force=True, silent=True) or {}
    raw_refresh = payload.get("refreshToken")
    if raw_refresh:
        with get_session() as session:
            session.execute(
                text("CALL sp_revoke_refresh_token(:token_hash)"),
                {"token_hash": _hash_token(raw_refresh)}
            )
            session.commit()
    return success({"loggedOut": True}, status_code=200, message="Logged out successfully")
