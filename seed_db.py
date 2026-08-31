"""Seeds a freshly-migrated database with the static/reference data the
frontend expects to exist on first load: roles, role_page_access dynamic menus,
subscription plans, badge catalog, an ADMIN account, sample teacher for PTC,
and the 8 runbooks ported from runbooks.ts.

Usage:
    python seed_db.py
"""
import json
import os
import uuid

from datetime import datetime
from sqlalchemy import text

from database.dbConnection import get_session, init_db
from model.models import SubscriptionPlan, Badge, User, Teacher, Runbook, Role, RolePageAccess
from utils.security import hash_password

SEED_RUNBOOKS_PATH = os.path.join(os.path.dirname(__file__), "sql", "seed_runbooks.json")

ROLES = [
    {"id": 1, "role_name": "Student", "is_active": True},
    {"id": 2, "role_name": "Parent", "is_active": True},
    {"id": 3, "role_name": "Teacher", "is_active": True},
    {"id": 4, "role_name": "Admin", "is_active": True},
]

ROLE_PAGES = [
    # 1. Student Persona Navigation
    {"role_id": 1, "page_name": "10-Mark Exam Arena", "page_route": "/arena", "icon": "Play", "menu_order": 1},
    {"role_id": 1, "page_name": "Adaptive Learning Path", "page_route": "/learning-path", "icon": "Compass", "menu_order": 2},
    {"role_id": 1, "page_name": "Ranks & Badges", "page_route": "/gamification", "icon": "Trophy", "menu_order": 3},
    {"role_id": 1, "page_name": "Brain Breaks & Games", "page_route": "/fun-zone", "icon": "Smile", "menu_order": 4},
    {"role_id": 1, "page_name": "Results & Analysis", "page_route": "/results", "icon": "Award", "menu_order": 5},

    # 2. Parent Persona Navigation
    {"role_id": 2, "page_name": "Family Dashboard", "page_route": "/dashboard", "icon": "BarChart3", "menu_order": 1},
    {"role_id": 2, "page_name": "Child Profiles", "page_route": "/children", "icon": "Users", "menu_order": 2},
    {"role_id": 2, "page_name": "Parent-Teacher Hub", "page_route": "/ptc", "icon": "MessageSquare", "menu_order": 3},
    {"role_id": 2, "page_name": "Subscription Plans", "page_route": "/pricing", "icon": "Sparkles", "menu_order": 4},
    {"role_id": 2, "page_name": "10-Mark Exam Arena", "page_route": "/arena", "icon": "Play", "menu_order": 5},
    {"role_id": 2, "page_name": "Adaptive Path Overview", "page_route": "/learning-path", "icon": "Compass", "menu_order": 6},
    {"role_id": 2, "page_name": "Curriculum Blog", "page_route": "/blog", "icon": "BookOpen", "menu_order": 7},

    # 3. Teacher Persona Navigation
    {"role_id": 3, "page_name": "Teacher Communication Portal", "page_route": "/ptc", "icon": "MessageSquare", "menu_order": 1},
    {"role_id": 3, "page_name": "Student Diagnostic Dossiers", "page_route": "/dossiers", "icon": "FileText", "menu_order": 2},

    # 4. Admin Persona Navigation
    {"role_id": 4, "page_name": "Super Admin Console", "page_route": "/admin", "icon": "ShieldCheck", "menu_order": 1},
    {"role_id": 4, "page_name": "RAG Runbook Engine", "page_route": "/runbooks", "icon": "Layers", "menu_order": 2},
    {"role_id": 4, "page_name": "Family Dashboard", "page_route": "/dashboard", "icon": "BarChart3", "menu_order": 3},
    {"role_id": 4, "page_name": "10-Mark Exam Arena", "page_route": "/arena", "icon": "Play", "menu_order": 4},
]

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
        # 1. Seed Roles
        for r_data in ROLES:
            existing = session.query(Role).filter(Role.role_name == r_data["role_name"]).first()
            if not existing:
                session.add(Role(id=r_data["id"], role_name=r_data["role_name"], is_active=r_data["is_active"]))
        session.flush()

        # 2. Seed Role Dynamic Menus
        for page_data in ROLE_PAGES:
            existing = session.query(RolePageAccess).filter(
                RolePageAccess.role_id == page_data["role_id"],
                RolePageAccess.page_route == page_data["page_route"],
            ).first()
            if not existing:
                session.add(RolePageAccess(
                    role_id=page_data["role_id"],
                    page_name=page_data["page_name"],
                    page_route=page_data["page_route"],
                    icon=page_data["icon"],
                    menu_order=page_data["menu_order"],
                    is_active=True,
                ))
        session.flush()

        # 3. Seed Subscription Plans
        for plan_data in SUBSCRIPTION_PLANS:
            existing = session.get(SubscriptionPlan, plan_data["id"])
            if existing:
                continue
            session.add(SubscriptionPlan(**plan_data))

        # 4. Seed Badges
        for badge_data in BADGES:
            if session.get(Badge, badge_data["id"]):
                continue
            session.add(Badge(**badge_data))

        # 5. Seed Admin User
        admin_email = "admin123@acugrade.ai"
        existing_admin = session.query(User).filter((User.email == admin_email) | (User.name == "Admin123")).first()
        if not existing_admin:
            admin_user = User(
                name="Admin123",
                email=admin_email,
                password_hash=hash_password("admin1234"),
                role_id=4,  # ADMIN
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(admin_user)
            print("Created ADMIN (Username: Admin123 / Email: admin123@acugrade.ai / Password: admin1234)")

        # 6. Seed Sample Teacher
        sample_teacher_email = "teacher.priya@acugrade.ai"
        teacher_user = session.query(User).filter(User.email == sample_teacher_email).first()
        if not teacher_user:
            teacher_user = User(
                name="Priya Sharma",
                email=sample_teacher_email,
                password_hash=hash_password("ChangeMe123!"),
                role_id=3,  # TEACHER
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(teacher_user)
            session.flush()
            session.add(Teacher(
                id=teacher_user.id,
                role_title="Mathematics Teacher",
                subject="Mathematics",
                school_name="Delhi Public School, R.K. Puram",
                verified=True,
            ))

        # 7. Seed Runbooks
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
                id=str(uuid.uuid4()),
                board=rb_data["board"],
                class_grade=rb_data["class_grade"],
                subject=rb_data["subject"],
                chapter_name=rb_data["chapter_name"],
                core_concepts=rb_data["core_concepts"],
                key_formulas_or_rules=rb_data["key_formulas_or_rules"],
                common_traps=rb_data["common_traps"],
                curated_reference_urls=rb_data["curated_reference_urls"],
                sample_question_archetypes=rb_data["sample_question_archetypes"],
                difficulty_calibration=rb_data["difficulty_calibration"],
                status="PUBLISHED",
            ))

    print("Seed complete.")


if __name__ == "__main__":
    seed()
