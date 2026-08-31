from flask import Blueprint, request, g

from database.dbConnection import get_session
from helper.gamification_engine import award_xp
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import assert_owns_student
from model.models import Badge, Student
from utils.errors import ValidationError
from utils.response import success
from utils.serializers import badge_to_dict
from utils.validators import require_fields

gamification_bp = Blueprint("gamification", __name__, url_prefix="/api/v1/gamification")


@gamification_bp.get("/badges")
def list_badges():
    """Public catalog read — badge definitions aren't sensitive."""
    with get_session() as session:
        badges = session.query(Badge).all()
        return success([badge_to_dict(b) for b in badges])


@gamification_bp.post("/award-xp")
@token_required
def award_xp_route():
    """Backs the frontend's Fun Zone mini-games (`onAwardXP`). The amount is
    still client-reported here since Fun Zone games run entirely client-side
    with no server-verifiable outcome — capped server-side to prevent abuse,
    unlike exam XP which is fully server-computed in exam_controller.py."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["studentId", "amount", "reason"])

    amount = int(payload["amount"])
    if amount <= 0 or amount > 100:
        raise ValidationError("XP award amount must be between 1 and 100")

    with get_session() as session:
        if g.current_user_role == "STUDENT":
            if payload["studentId"] != g.current_user_id:
                raise ValidationError("Students may only award XP to themselves")
            student = session.get(Student, g.current_user_id)
        else:
            student = assert_owns_student(session, payload["studentId"], g.current_user_id)

        award_xp(session, student, amount, str(payload["reason"])[:190])
        return success({"xp": student.xp, "level": student.level})
