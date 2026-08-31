"""Role-based access control. Always stacked *under* @token_required so
g.current_user_role is already populated."""
from functools import wraps

from flask import g

from utils.errors import ForbiddenError


def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = getattr(g, "current_user_role", None)
            if role not in allowed_roles:
                raise ForbiddenError(f"This action requires one of: {', '.join(allowed_roles)}")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def assert_owns_student(session, student_id: str, parent_user_id: str):
    """Object-level authorization: a parent may only touch their own children.
    Master prompt §8 — this is the concrete enforcement of that rule."""
    from model.models import Student
    from utils.errors import ForbiddenError, NotFoundError

    student = session.get(Student, student_id)
    if not student:
        raise NotFoundError("Student not found")
    if student.parent_id != parent_user_id:
        raise ForbiddenError("You do not have access to this student")
    return student
