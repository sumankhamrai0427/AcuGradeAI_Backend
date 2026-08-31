import re

from utils.constants import BOARDS, CLASS_GRADES, SUBJECTS, DIFFICULTIES
from utils.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_fields(payload: dict, fields: list[str]):
    missing = [f for f in fields if payload.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_email(email: str):
    if not email or not EMAIL_RE.match(email):
        raise ValidationError("Invalid email address")


def validate_password_strength(password: str):
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")


def validate_enum(value: str, allowed: list[str], field_name: str):
    if value not in allowed:
        raise ValidationError(f"Invalid {field_name}: '{value}'. Must be one of {allowed}")


def validate_board(value: str):
    validate_enum(value, BOARDS, "board")


def validate_class_grade(value: str):
    validate_enum(value, CLASS_GRADES, "classGrade")


def validate_subject(value: str):
    validate_enum(value, SUBJECTS, "subject")


def validate_difficulty(value: str):
    validate_enum(value, DIFFICULTIES, "difficulty")


def validate_pin(pin: str):
    if not pin or not re.match(r"^\d{4,6}$", pin):
        raise ValidationError("PIN must be 4-6 digits")
