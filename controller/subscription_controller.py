from flask import request, g

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import SubscriptionPlan, Parent
from utils.errors import ValidationError
from utils.response import success
from utils.validators import require_fields


def _plan_to_dict(plan: SubscriptionPlan) -> dict:
    return {
        "id": plan.id,
        "name": plan.name,
        "priceMonthly": float(plan.price_monthly),
        "priceYearly": float(plan.price_yearly),
        "currency": plan.currency,
        "badge": plan.badge,
        "description": plan.description,
        "features": plan.features,
        "dailyExamLimit": "unlimited" if plan.daily_exam_limit == "unlimited" else int(plan.daily_exam_limit),
        "maxChildren": "unlimited" if plan.max_children == "unlimited" else int(plan.max_children),
        "isPopular": bool(plan.is_popular),
    }


def list_plans():
    """Public — pricing pages don't require auth."""
    with get_session() as session:
        plans = session.query(SubscriptionPlan).all()
        return success([_plan_to_dict(p) for p in plans])


@token_required
@roles_required("PARENT")
def upgrade_plan():
    """NOTE: this only changes the tier flag; no payment processor is wired
    up here (the master prompt doesn't specify one, and the original
    frontend has no payment UI either — see docs/FRONTEND_BACKEND_MAPPING.md
    §2.7). Treat this as an admin/self-service tier change until real
    billing is integrated."""
    payload = request.get_json(force=True, silent=True) or {}
    require_fields(payload, ["tier"])

    with get_session() as session:
        plan = session.get(SubscriptionPlan, payload["tier"])
        if not plan:
            raise ValidationError(f"Unknown subscription tier '{payload['tier']}'")

        parent = session.get(Parent, g.current_user_id)
        parent.subscription_tier = plan.id
        return success({"subscriptionTier": parent.subscription_tier})

