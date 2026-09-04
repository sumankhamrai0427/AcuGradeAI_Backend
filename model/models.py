"""SQLAlchemy ORM models — one-to-one with sql/schema.sql."""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Enum, JSON,
    Numeric, Text, UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ------------------------------------------------------------
# 1. Roles & Dynamic Page Access
# ------------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="role")
    menu_items = relationship("RolePageAccess", back_populates="role", cascade="all, delete-orphan")


class RolePageAccess(Base):
    __tablename__ = "role_page_access"
    __table_args__ = (UniqueConstraint("role_id", "page_route", name="uq_role_page"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    page_name = Column(String(100), nullable=False)
    page_route = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    menu_order = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="menu_items")


# ------------------------------------------------------------
# 2. Users & auth
# ------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(190), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, nullable=True)

    role = relationship("Role", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# 3. Parent / Student / Teacher
# ------------------------------------------------------------
class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    subscription_tier = Column(
        Enum("free", "scholar_pro", "genius_competitive", name="subscription_tier"),
        nullable=False, default="free",
    )
    subscription_expiry = Column(DateTime, nullable=True)

    children = relationship("Student", back_populates="parent", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[id])


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    avatar = Column(String(20), default="🧑‍🎓")
    class_grade = Column(String(20), nullable=False)
    target_board = Column(String(20), nullable=False)
    school_name = Column(String(190), nullable=True)
    pin_hash = Column(String(255), nullable=False)
    daily_exams_taken_today = Column(Integer, default=0)
    last_exam_date = Column(Date, nullable=True)
    total_exams_taken = Column(Integer, default=0)
    average_score = Column(Numeric(4, 2), default=0)
    streak_days = Column(Integer, default=0)
    xp = Column(Integer, default=250)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Parent", back_populates="children")
    user = relationship("User", foreign_keys=[id])


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_title = Column(String(120), default="Subject Teacher")
    subject = Column(String(60), nullable=True)
    school_name = Column(String(190), nullable=False)
    phone = Column(String(30), nullable=True)
    verified = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[id])


# ------------------------------------------------------------
# 4. Curriculum / Runbooks
# ------------------------------------------------------------
class Runbook(Base):
    __tablename__ = "runbooks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    board = Column(String(20), nullable=False)
    class_grade = Column(String(20), nullable=False)
    subject = Column(String(40), nullable=False)
    chapter_name = Column(String(190), nullable=False)
    core_concepts = Column(JSON, nullable=False)
    key_formulas_or_rules = Column(JSON, nullable=False)
    common_traps = Column(JSON, nullable=False)
    curated_reference_urls = Column(JSON, nullable=False)
    sample_question_archetypes = Column(JSON, nullable=False)
    difficulty_calibration = Column(JSON, nullable=False)
    status = Column(Enum("DRAFT", "PUBLISHED", "ARCHIVED", name="runbook_status"), default="PUBLISHED")
    version = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    runbook_id = Column(String(36), ForeignKey("runbooks.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    board = Column(String(20), nullable=True)
    class_grade = Column(String(20), nullable=True)
    subject = Column(String(40), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum("PENDING", "PROCESSED", "FAILED", name="document_status"), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    vector_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# 5. Exams / Questions / Submissions
# ------------------------------------------------------------
class Exam(Base):
    __tablename__ = "exams"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    board = Column(String(20), nullable=False)
    class_grade = Column(String(20), nullable=False)
    subject = Column(String(40), nullable=False)
    difficulty = Column(Enum("simple", "medium", "hard", name="exam_difficulty"), nullable=False)
    total_marks = Column(Integer, default=10)
    question_count = Column(Integer, default=10)
    time_limit_minutes = Column(Integer, default=15)
    rag_knowledge_nodes_used = Column(JSON, nullable=True)
    source = Column(Enum("mistral-rag", "rag-engine-curated", name="exam_source"), nullable=False)
    status = Column(
        Enum("GENERATED", "IN_PROGRESS", "SUBMITTED", "EXPIRED", name="exam_status"),
        default="GENERATED",
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    exam_id = Column(String(36), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    type = Column(Enum("mcq", "objective", "numerical", "logical", name="question_type"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(500), nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(Enum("simple", "medium", "hard", name="question_difficulty"), nullable=False)
    marks = Column(Integer, default=1)
    topic = Column(String(190), nullable=False)
    reference_links = Column(JSON, nullable=True)
    hint = Column(Text, nullable=True)

    exam = relationship("Exam", back_populates="questions")


class ExamSubmission(Base):
    __tablename__ = "exam_submissions"
    __table_args__ = (UniqueConstraint("exam_id", name="uq_submission_per_exam"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    exam_id = Column(String(36), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    answers = Column(JSON, nullable=False)
    marks_obtained = Column(Integer, nullable=False)
    total_marks = Column(Integer, default=10)
    accuracy_percentage = Column(Numeric(5, 2), nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("QuestionEvaluation", cascade="all, delete-orphan")
    analysis = relationship("DiagnosticAnalysis", uselist=False, cascade="all, delete-orphan")
    exam = relationship("Exam")
    student = relationship("Student")


class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    submission_id = Column(String(36), ForeignKey("exam_submissions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    student_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    marks_awarded = Column(Integer, nullable=False)
    misconception_identified = Column(String(255), nullable=True)

    question = relationship("Question")


class DiagnosticAnalysis(Base):
    __tablename__ = "diagnostic_analyses"
    __table_args__ = (UniqueConstraint("submission_id", name="uq_diag_per_submission"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    submission_id = Column(String(36), ForeignKey("exam_submissions.id", ondelete="CASCADE"), nullable=False)
    overall_band = Column(
        Enum("Needs Foundation", "Developing", "Proficient", "Advanced Mastery", "Competitive Ready",
             name="diagnostic_band"),
        nullable=False,
    )
    mastery_score_percentage = Column(Numeric(5, 2), nullable=False)
    strengths = Column(JSON, nullable=False)
    areas_to_improve = Column(JSON, nullable=False)
    k_graph_insights = Column(JSON, nullable=False)
    evolutionary_roadmap = Column(Text, nullable=False)
    encouragement_note = Column(Text, nullable=False)
    recommended_next_exam = Column(JSON, nullable=False)
    curated_study_links = Column(JSON, nullable=False)
    source = Column(Enum("mistral", "fallback", name="diagnostic_source"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# 6. Mastery / Misconceptions / Learning path
# ------------------------------------------------------------
class Mastery(Base):
    __tablename__ = "mastery"
    __table_args__ = (UniqueConstraint("student_id", "topic", name="uq_mastery_student_topic"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(190), nullable=False)
    mastery_score = Column(Numeric(5, 2), default=0)
    confidence = Column(Numeric(5, 2), default=0)
    attempt_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    status = Column(
        Enum("NOT_STARTED", "LEARNING", "DEVELOPING", "MASTERED", "CRITICAL_GAP", name="mastery_status"),
        default="NOT_STARTED",
    )
    last_assessed_at = Column(DateTime, nullable=True)


class Misconception(Base):
    __tablename__ = "misconceptions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(190), nullable=False)
    description = Column(String(500), nullable=False)
    evidence = Column(Text, nullable=True)
    severity = Column(Enum("LOW", "MEDIUM", "HIGH", name="misconception_severity"), default="MEDIUM")
    status = Column(Enum("OPEN", "IMPROVING", "RESOLVED", name="misconception_status"), default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(190), nullable=False)
    chapter_name = Column(String(190), nullable=False)
    subject = Column(String(40), nullable=False)
    class_grade = Column(String(20), nullable=False)
    board = Column(String(20), nullable=False)
    status = Column(
        Enum("locked", "available", "in_progress", "mastered", "remedial_needed", name="lp_status"),
        default="available",
    )
    mastery_percentage = Column(Numeric(5, 2), default=0)
    level = Column(Enum("foundational", "intermediate", "advanced_hots", name="lp_level"), default="foundational")
    prerequisites = Column(JSON, nullable=True)
    key_concepts = Column(JSON, nullable=True)
    common_misconceptions = Column(JSON, nullable=True)
    curated_resources = Column(JSON, nullable=True)
    practice_exam_config = Column(JSON, nullable=True)
    recommended_reason = Column(String(500), nullable=True)
    attempts_count = Column(Integer, default=0)
    last_score = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ------------------------------------------------------------
# 7. Gamification
# ------------------------------------------------------------
class Badge(Base):
    __tablename__ = "badges"

    id = Column(String(60), primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(20), nullable=False)
    tier = Column(Enum("bronze", "silver", "gold", "diamond", name="badge_tier"), nullable=False)
    category = Column(Enum("mastery", "streak", "score", "speed", "explorer", name="badge_category"), nullable=False)
    xp_reward = Column(Integer, default=0)
    requirement_text = Column(String(255), nullable=False)


class StudentBadge(Base):
    __tablename__ = "student_badges"

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    badge_id = Column(String(60), ForeignKey("badges.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow)


class XPEvent(Base):
    __tablename__ = "xp_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(190), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# 8. Parent-teacher communication
# ------------------------------------------------------------
class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("parent_id", "teacher_id", "student_id", name="uq_conv"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                             order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_role = Column(Enum("parent", "teacher", name="sender_role"), nullable=False)
    sender_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    attached_submission_id = Column(String(36), ForeignKey("exam_submissions.id", ondelete="SET NULL"), nullable=True)
    action_items = Column(JSON, nullable=True)
    status = Column(Enum("sent", "delivered", "read", "action_taken", name="message_status"), default="sent")
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class SharedDossier(Base):
    __tablename__ = "shared_dossiers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    share_token = Column(String(60), nullable=False, unique=True)
    notes = Column(Text, nullable=True)
    recipients = Column(JSON, nullable=False)
    included_submissions_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime, nullable=True)
    status = Column(Enum("active", "revoked", name="dossier_status"), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    student = relationship("Student", foreign_keys=[student_id])
    parent = relationship("Parent", foreign_keys=[parent_id])


class PTMSchedule(Base):
    __tablename__ = "ptm_schedules"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    topic = Column(String(255), nullable=False)
    meeting_link = Column(String(255), nullable=True)
    status = Column(Enum("SCHEDULED", "COMPLETED", "CANCELLED", name="ptm_status"), default="SCHEDULED")
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Parent")
    teacher = relationship("Teacher")
    student = relationship("Student")


# ------------------------------------------------------------
# 9. Subscriptions
# ------------------------------------------------------------
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String(30), primary_key=True)
    name = Column(String(150), nullable=False)
    price_monthly = Column(Numeric(8, 2), nullable=False)
    price_yearly = Column(Numeric(8, 2), nullable=False)
    currency = Column(String(10), default="USD")
    badge = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    features = Column(JSON, nullable=False)
    daily_exam_limit = Column(String(20), nullable=False)
    max_children = Column(String(20), nullable=False)
    is_popular = Column(Boolean, default=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(String(30), ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(Enum("ACTIVE", "EXPIRED", "CANCELLED", name="subscription_status"), default="ACTIVE")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)


# ------------------------------------------------------------
# 10. Audit
# ------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(120), nullable=False)
    entity_type = Column(String(60), nullable=True)
    entity_id = Column(String(60), nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# 11. Master Tables
# ------------------------------------------------------------
class BoardMaster(Base):
    __tablename__ = "board_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClassMaster(Base):
    __tablename__ = "class_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

