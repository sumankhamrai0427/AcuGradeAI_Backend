import json
import random
import uuid
from datetime import datetime

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from helper import fallback_exam_bank, rag_engine
from model import mistral_client
from model.models import Exam, Question, Mastery
from prompts import exam_generation_prompt
from utils.ai_schemas import GeneratedExamSchema
from utils.constants import (
    DEFAULT_EXAM_QUESTION_COUNT, DEFAULT_EXAM_TOTAL_MARKS, DEFAULT_EXAM_TIME_LIMIT_MINUTES,
)
from utils.logger import logger


def get_weak_topics(session: Session, student_id: str, threshold: float = 75.0) -> list[str]:
    rows = session.query(Mastery).filter(
        Mastery.student_id == student_id, Mastery.mastery_score < threshold
    ).all()
    return [row.topic for row in rows]


def _fetch_questions_from_db(
    session: Session,
    *,
    board: str,
    class_grade: str,
    subject: str,
    difficulty: str,
) -> list[dict]:
    """Fetches real-time curriculum questions directly via Stored Procedure
    `sp_generate_exam_from_db` without any inline SQL queries.
    """
    clean_board = (board or "").strip()
    clean_class = (class_grade or "").strip()
    clean_subj = (subject or "").strip()
    clean_diff = (difficulty or "medium").strip()

    sp_rows = session.execute(
        text("CALL sp_generate_exam_from_db(:board, :class_grade, :subject, :difficulty)"),
        {
            "board": clean_board,
            "class_grade": clean_class,
            "subject": clean_subj,
            "difficulty": clean_diff,
        },
    ).mappings().fetchall()

    if not sp_rows:
        return []

    # Format questions into standard structure
    formatted_questions = []
    for idx, q in enumerate(sp_rows):
        raw_options = q.get("options")
        options_list = None
        if raw_options:
            if isinstance(raw_options, list):
                options_list = raw_options
            elif isinstance(raw_options, str):
                try:
                    parsed = json.loads(raw_options)
                    if isinstance(parsed, list):
                        options_list = parsed
                    elif isinstance(parsed, dict):
                        options_list = [f"{k}) {v}" for k, v in parsed.items()]
                except Exception:
                    options_list = [opt.strip() for opt in raw_options.split("|") if opt.strip()]

        raw_type = str(q.get("question_type", "mcq")).lower()
        raw_marks = int(q.get("marks", 1))

        if "saq" in raw_type or "short" in raw_type or raw_marks == 2:
            final_type = "saq"
            final_marks = 2
        elif "num" in raw_type:
            final_type = "numerical"
            final_marks = 1
        elif "logic" in raw_type:
            final_type = "logical"
            final_marks = 1
        elif "obj" in raw_type and not options_list:
            final_type = "objective"
            final_marks = 1
        else:
            final_type = "mcq"
            final_marks = 1

        formatted_questions.append({
            "questionNumber": idx + 1,
            "type": final_type,
            "questionText": q.get("question_text", f"Question {idx + 1}"),
            "options": options_list,
            "correctAnswer": str(q.get("correct_answer", "A")),
            "explanation": q.get("explanation") or "Answer derived from standard curriculum textbook concepts.",
            "topic": q.get("topic_name") or q.get("chapter_name") or clean_subj,
            "difficulty": q.get("difficulty") or clean_diff,
            "marks": final_marks,
        })

    return formatted_questions


def generate_exam(
    session: Session,
    *,
    student_id: str,
    student_name: str,
    board: str,
    class_grade: str,
    subject: str,
    difficulty: str,
) -> Exam:
    weak_topics = get_weak_topics(session, student_id)
    matching_runbooks = rag_engine.retrieve_runbooks(session, board, class_grade, subject)
    rag_context = rag_engine.runbooks_to_context(matching_runbooks, difficulty)

    # ------------------------------------------------------------
    # 1. Primary Generation Layer: Relational Database Question Bank
    # ------------------------------------------------------------
    questions_data = _fetch_questions_from_db(
        session,
        board=board,
        class_grade=class_grade,
        subject=subject,
        difficulty=difficulty,
    )
    source = "rag-engine-curated"

    # ------------------------------------------------------------
    # 2. Secondary Layer: LLM + RAG (kept inactive during initial launch)
    # ------------------------------------------------------------
    USE_LLM_LAYER = False
    if not questions_data and USE_LLM_LAYER and mistral_client.is_configured():
        try:
            user_prompt = exam_generation_prompt.build_user_prompt(
                board=board, class_grade=class_grade, subject=subject, difficulty=difficulty,
                student_name=student_name, weak_topics=weak_topics, rag_context=rag_context,
            )
            raw = mistral_client.generate_json(exam_generation_prompt.SYSTEM_PROMPT, user_prompt)
            validated = GeneratedExamSchema.model_validate(raw)
            questions_data = [q.model_dump() for q in validated.questions][:DEFAULT_EXAM_QUESTION_COUNT]
            source = "mistral-rag"
        except (mistral_client.MistralUnavailableError, PydanticValidationError) as exc:
            logger.error(f"Exam generation via Mistral failed, using fallback: {exc}")

    # Determine class-based marks blueprint
    cg_lower = (class_grade or "").lower()
    if any(c in cg_lower for c in ["class 1", "class 2", "class 3", "class 4"]):
        default_grade_marks = 5
        duration_mins = 10
    elif any(c in cg_lower for c in ["class 11", "class 12", "neet", "iit"]):
        default_grade_marks = 20
        duration_mins = 25
    elif any(c in cg_lower for c in ["class 9", "class 10"]):
        default_grade_marks = 15
        duration_mins = 20
    else:
        default_grade_marks = 15
        duration_mins = 15

    calculated_marks = sum(int(q.get("marks", 1)) for q in questions_data) if questions_data and any("marks" in q for q in questions_data) else default_grade_marks

    # ------------------------------------------------------------
    # 3. Deterministic Fallback Bank (Safety backup)
    # ------------------------------------------------------------
    if not questions_data:
        ref_links = matching_runbooks[0].curated_reference_urls if matching_runbooks else []
        questions_data = fallback_exam_bank.build_fallback_questions(board, subject, difficulty, ref_links)
        source = "rag-engine-curated"

    title = f"{class_grade} {board} {subject} ({difficulty.upper()}) Diagnostic {calculated_marks}-Mark Exam"

    exam = Exam(
        id=str(uuid.uuid4()),
        student_id=student_id,
        title=title,
        board=board,
        class_grade=class_grade,
        subject=subject,
        difficulty=difficulty,
        total_marks=calculated_marks,
        question_count=len(questions_data),
        time_limit_minutes=DEFAULT_EXAM_TIME_LIMIT_MINUTES,
        rag_knowledge_nodes_used=[rb.chapter_name for rb in matching_runbooks],
        source=source,
        status="GENERATED",
        created_at=datetime.utcnow(),
    )
    session.add(exam)
    session.flush()

    ref_links_default = matching_runbooks[0].curated_reference_urls if matching_runbooks else []
    for idx, q in enumerate(questions_data):
        # Appended through the relationship (not just given a raw exam_id)
        # so SQLAlchemy's in-memory `exam.questions` collection stays in
        # sync — setting exam_id alone leaves the ORM's cached collection
        # stale even though the FK is correct in the database.
        q_diff = str(q.get("difficulty") or difficulty).lower()
        if q_diff not in ("simple", "medium", "hard"):
            q_diff = "medium"

        exam.questions.append(
            Question(
                id=str(uuid.uuid4()),
                question_number=idx + 1,
                type=q.get("type", "mcq"),
                question_text=q.get("questionText", f"Question {idx + 1}"),
                options=q.get("options"),
                correct_answer=str(q.get("correctAnswer", "A")),
                explanation=q.get("explanation", "Detailed step explanation."),
                difficulty=q_diff,
                marks=int(q.get("marks", 1)),
                topic=q.get("topic", subject),
                reference_links=ref_links_default,
                hint=q.get("hint"),
            )
        )
    session.flush()

    return exam


def exam_to_public_dict(exam: Exam) -> dict:
    """Client-facing exam shape — never includes correct_answer or explanation."""
    return {
        "id": exam.id,
        "title": exam.title,
        "board": exam.board,
        "classGrade": exam.class_grade,
        "subject": exam.subject,
        "difficulty": exam.difficulty,
        "totalMarks": exam.total_marks,
        "questionCount": exam.question_count,
        "timeLimitMinutes": exam.time_limit_minutes,
        "ragKnowledgeNodesUsed": exam.rag_knowledge_nodes_used or [],
        "createdAt": exam.created_at.isoformat(),
        "questions": [
            {
                "id": q.id,
                "questionNumber": q.question_number,
                "type": q.type,
                "questionText": q.question_text,
                "options": q.options,
                "difficulty": q.difficulty,
                "marks": q.marks,
                "topic": q.topic,
                "hint": q.hint,
                # NOTE: correctAnswer / explanation deliberately omitted (§14).
            }
            for q in sorted(exam.questions, key=lambda x: x.question_number)
        ],
    }
