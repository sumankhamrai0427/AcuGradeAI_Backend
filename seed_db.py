"""Seeds a freshly-migrated database with the static/reference data the
frontend expects to exist on first load: subscription plans, badge catalog,
a SUPER_ADMIN account, the 8 runbooks ported from the frontend's
runbooks.ts, and one sample teacher for the PTC feature to have someone to
message. Safe to re-run — every insert is upsert-by-id.

Usage:
    python seed_db.py
"""
import json
import os
import uuid

from database.dbConnection import get_session, init_db
from model.models import SubscriptionPlan, Badge, User, Teacher, Runbook
from utils.security import hash_password

SEED_RUNBOOKS_PATH = os.path.join(os.path.dirname(__file__), "sql", "seed_runbooks.json")

SUBSCRIPTION_PLANS = [
    {
        "id": "free", "name": "Foundation Free", "price_monthly": 0, "price_yearly": 0,
        "currency": "USD", "badge": None,
        "description": "Perfect for daily revision and steady concept checking across school subjects.",
        "features": [
            "1 exam (10 marks) per day per child",
            "All 8 Boards (CBSE, ICSE, ISC, Cambridge, NCERT, NEET, IIT)",
            "Basic answer key & score breakdown",
            "Up to 2 child sub-accounts",
            "Community knowledge base access",
        ],
        "daily_exam_limit": "1", "max_children": "2", "is_popular": False,
    },
    {
        "id": "scholar_pro", "name": "Scholar Pro", "price_monthly": 9, "price_yearly": 89,
        "currency": "USD", "badge": "Most Popular for School Students",
        "description": "Comprehensive adaptive AI-RAG learning with evolutionary topic mastery tracking.",
        "features": [
            "Unlimited 10-mark diagnostic exams daily",
            "Full AI-RAG Misconception & Error Classification",
            "Curated Official Syllabus Reference Links & Video Guides",
            "Evolutionary Subject K-Graph Mastery Tracker",
            "Up to 5 child sub-accounts with separate PINs",
            "Detailed Parent Performance Analytical Reports",
            "Downloadable & Printable PDF Diagnostic Dossiers",
        ],
        "daily_exam_limit": "unlimited", "max_children": "5", "is_popular": True,
    },
    {
        "id": "genius_competitive", "name": "Genius Competitive (NEET / IIT / Cambridge)",
        "price_monthly": 19, "price_yearly": 189, "currency": "USD",
        "badge": "For Olympiad, NEET & JEE Aspirants",
        "description": "Deep analytical testing engine with high-order thinking (HOTS) and Olympiad difficulty.",
        "features": [
            "Everything in Scholar Pro + Unlimited Children",
            "High-Order Thinking (HOTS) & Olympiad Difficulty Drills",
            "Dedicated NEET NTA & IIT JEE Advanced Question Archetypes",
            "Custom Chapter Runbook & Blueprint Focus Mode",
            "Negative marking & speed velocity analytics",
            "Priority AI Reasoning",
            "1-on-1 Parent Consultation Summary Export",
        ],
        "daily_exam_limit": "unlimited", "max_children": "unlimited", "is_popular": False,
    },
]

BADGES = [
    {"id": "badge-pioneer", "title": "Pioneer", "description": "Took your first diagnostic exam.",
     "icon": "🚀", "tier": "bronze", "category": "explorer", "xp_reward": 0,
     "requirement_text": "Complete your first exam"},
    {"id": "badge-perfect-10", "title": "Perfect 10", "description": "Scored a flawless 10/10.",
     "icon": "🏆", "tier": "gold", "category": "score", "xp_reward": 50,
     "requirement_text": "Score 10/10 on any exam"},
    {"id": "badge-speed-demon", "title": "Speed Demon", "description": "Fast and accurate under 6 minutes.",
     "icon": "⚡", "tier": "silver", "category": "speed", "xp_reward": 25,
     "requirement_text": "Score 8+ in under 6 minutes"},
    {"id": "badge-streak-3", "title": "3-Day Streak", "description": "Three days of consistent practice.",
     "icon": "🔥", "tier": "bronze", "category": "streak", "xp_reward": 15,
     "requirement_text": "Maintain a 3-day streak"},
    {"id": "badge-streak-7", "title": "7-Day Streak", "description": "A full week of dedication.",
     "icon": "🔥", "tier": "gold", "category": "streak", "xp_reward": 40,
     "requirement_text": "Maintain a 7-day streak"},
    {"id": "badge-olympiad-thinker", "title": "Olympiad Thinker", "description": "Excelled at hard-difficulty questions.",
     "icon": "🧠", "tier": "diamond", "category": "mastery", "xp_reward": 60,
     "requirement_text": "Score 9+ on a hard-difficulty exam"},
]


def seed():
    init_db()

    with get_session() as session:
        for plan_data in SUBSCRIPTION_PLANS:
            existing = session.get(SubscriptionPlan, plan_data["id"])
            if existing:
                continue
            session.add(SubscriptionPlan(**plan_data))

        for badge_data in BADGES:
            if session.get(Badge, badge_data["id"]):
                continue
            session.add(Badge(**badge_data))

        admin_email = "admin@acugrade.ai"
        if not session.query(User).filter(User.email == admin_email).first():
            admin_id = str(uuid.uuid4())
            session.add(User(
                id=admin_id, name="AcuGrade Super Admin", email=admin_email,
                password_hash=hash_password("ChangeMe123!"), role="SUPER_ADMIN", status="ACTIVE",
            ))
            print(f"Created SUPER_ADMIN {admin_email} / ChangeMe123! — change this password immediately.")

        sample_teacher_email = "teacher.priya@acugrade.ai"
        if not session.query(User).filter(User.email == sample_teacher_email).first():
            teacher_id = str(uuid.uuid4())
            session.add(User(
                id=teacher_id, name="Priya Sharma", email=sample_teacher_email,
                password_hash=hash_password("ChangeMe123!"), role="TEACHER", status="ACTIVE",
            ))
            session.flush()
            session.add(Teacher(
                id=teacher_id, role_title="Mathematics Teacher", subject="Mathematics",
                school_name="Delhi Public School, R.K. Puram", verified=True,
            ))

        with open(SEED_RUNBOOKS_PATH, "r", encoding="utf-8") as f:
            runbook_defs = json.load(f)

        existing_chapters = {
            (rb.board, rb.class_grade, rb.subject, rb.chapter_name)
            for rb in session.query(Runbook).all()
        }
        for rb_data in runbook_defs:
            key = (rb_data["board"], rb_data["class_grade"], rb_data["subject"], rb_data["chapter_name"])
            if key in existing_chapters:
                continue
            session.add(Runbook(
                id=str(uuid.uuid4()), board=rb_data["board"], class_grade=rb_data["class_grade"],
                subject=rb_data["subject"], chapter_name=rb_data["chapter_name"],
                core_concepts=rb_data["core_concepts"], key_formulas_or_rules=rb_data["key_formulas_or_rules"],
                common_traps=rb_data["common_traps"], curated_reference_urls=rb_data["curated_reference_urls"],
                sample_question_archetypes=rb_data["sample_question_archetypes"],
                difficulty_calibration=rb_data["difficulty_calibration"], status="PUBLISHED",
            ))

    print("Seed complete.")


if __name__ == "__main__":
    seed()
