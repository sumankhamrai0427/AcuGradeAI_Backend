"""Orchestrates exam generation end-to-end, per master prompt §13's flow:
Auth -> Authorization -> Subscription/Quota -> Mastery -> Weak Topics ->
Runbook Retrieval -> RAG Retrieval -> Prompt -> Mistral -> Validation ->
Database -> Response.
"""
import uuid
from datetime import datetime

from pydantic import ValidationError as PydanticValidationError
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

    questions_data = None
    source = "rag-engine-curated"

    if mistral_client.is_configured():
        try:
            user_prompt = exam_generation_prompt.build_user_prompt(
                board=board, class_grade=class_grade, subject=subject, difficulty=difficulty,
                student_name=student_name, weak_topics=weak_topics, rag_context=rag_context,
            )
            raw = mistral_client.generate_json(exam_generation_prompt.SYSTEM_PROMPT, user_prompt)
            validated = GeneratedExamSchema.model_validate(raw)
            questions_data = [q.model_dump() for q in validated.questions][:DEFAULT_EXAM_QUESTION_COUNT]
            source = "mistral-rag"
            title = validated.title
        except (mistral_client.MistralUnavailableError, PydanticValidationError) as exc:
            logger.error(f"Exam generation via Mistral failed, using fallback: {exc}")

    if not questions_data:
        ref_links = matching_runbooks[0].curated_reference_urls if matching_runbooks else []
        questions_data = fallback_exam_bank.build_fallback_questions(board, subject, difficulty, ref_links)
        title = f"{class_grade} {board} {subject} ({difficulty.upper()}) Diagnostic 10-Mark Exam"

    exam = Exam(
        id=str(uuid.uuid4()),
        student_id=student_id,
        title=title,
        board=board,
        class_grade=class_grade,
        subject=subject,
        difficulty=difficulty,
        total_marks=DEFAULT_EXAM_TOTAL_MARKS,
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
        exam.questions.append(
            Question(
                id=str(uuid.uuid4()),
                question_number=idx + 1,
                type=q.get("type", "mcq"),
                question_text=q.get("questionText", f"Question {idx + 1}"),
                options=q.get("options"),
                correct_answer=str(q.get("correctAnswer", "A")),
                explanation=q.get("explanation", "Detailed step explanation."),
                difficulty=difficulty,
                marks=1,
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
