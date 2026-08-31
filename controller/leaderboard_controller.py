from flask import Blueprint, request

from database.dbConnection import get_session
from helper.gamification_engine import get_leaderboard
from utils.errors import ValidationError
from utils.response import success

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api/v1/leaderboard")

VALID_PERIODS = {"daily", "weekly", "monthly", "all_time"}


@leaderboard_bp.get("")
def leaderboard():
    period = request.args.get("period", "all_time")
    if period not in VALID_PERIODS:
        raise ValidationError(f"period must be one of {sorted(VALID_PERIODS)}")

    with get_session() as session:
        return success(get_leaderboard(session, period=period))
