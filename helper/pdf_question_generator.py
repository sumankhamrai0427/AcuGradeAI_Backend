"""AI-powered Question Extractor & Generator from uploaded documents/PDFs.
Reads document chunks and uses LLM to generate structured questions for question_master.
"""
import json
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from model import mistral_client
from model.models import Document, DocumentChunk
from utils.logger import logger


SYSTEM_PROMPT = """You are an expert curriculum designer and academic examiner.
Your task is to analyze the provided textbook/curriculum text and generate high-quality, pedagogically sound examination questions.

CRITICAL RULES:
1. Every question must be directly answerable and grounded ONLY in the provided text.
2. For MCQ (Multiple Choice Questions), provide exactly 4 distinct options labeled 'A) ', 'B) ', 'C) ', and 'D) '.
3. 'correct_answer' must be the letter of the correct option ('A', 'B', 'C', or 'D') or the full option text matching the letter.
4. 'explanation' must be a clear, concise justification explaining why the answer is correct and citing key facts from the text.
5. 'difficulty' must be one of: 'easy', 'medium', 'hard'.
6. 'marks' should default to 1 for MCQ / True-False, or 2-5 for Short Answer.
7. Return strictly a JSON object with a "questions" array. No Markdown formatting or commentary outside JSON.

JSON Schema:
{
  "questions": [
    {
      "question": "What is the primary function of chlorophyll in photosynthesis?",
      "type": "MCQ",
      "difficulty": "medium",
      "marks": 1,
      "options": [
        "A) To absorb sunlight energy",
        "B) To produce carbon dioxide",
        "C) To store water in roots",
        "D) To release nitrogen into air"
      ],
      "correct_answer": "A",
      "explanation": "Chlorophyll pigments absorb sunlight which drives the light-dependent reactions of photosynthesis.",
      "topic_suggested": "Photosynthesis"
    }
  ]
}
"""


def extract_curriculum_text(session: Session, document_id: str, max_chars: int = 12000) -> tuple[str, dict]:
    """Fetches document chunks and metadata for prompting."""
    doc = session.get(Document, document_id)
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    chunks = (
        session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    if not chunks:
        raise ValueError("No text content or chunks found for this document.")

    combined_text = []
    total_len = 0
    for chunk in chunks:
        c_text = chunk.content.strip()
        if total_len + len(c_text) > max_chars:
            # Append partial to reach max_chars
            combined_text.append(c_text[: max_chars - total_len])
            break
        combined_text.append(c_text)
        total_len += len(c_text)

    full_text = "\n\n".join(combined_text)
    metadata = {
        "id": doc.id,
        "filename": doc.filename,
        "board": doc.board or "",
        "classGrade": doc.class_grade or "",
        "subject": doc.subject or "",
    }
    return full_text, metadata


def generate_questions_from_doc(
    session: Session,
    document_id: str,
    count: int = 5,
    question_type: str = "MCQ",
    difficulty: str = "medium",
    custom_instructions: str = ""
) -> List[Dict[str, Any]]:
    """Generates structured questions from document chunks using the active LLM."""
    raw_text, meta = extract_curriculum_text(session, document_id)

    user_prompt = f"""Target Curriculum Details:
- Board: {meta.get('board', 'General')}
- Class / Grade: {meta.get('classGrade', 'Standard')}
- Subject: {meta.get('subject', 'General')}
- Requested Question Count: {count}
- Question Type: {question_type}
- Difficulty Level: {difficulty}

{f"Additional Instructions: {custom_instructions}" if custom_instructions else ""}

--- DOCUMENT EXCERPT ---
{raw_text}
--- END DOCUMENT EXCERPT ---

Please generate {count} examination questions based strictly on the text above. Output strictly JSON with the "questions" key."""

    try:
        response_json = mistral_client.generate_json(SYSTEM_PROMPT, user_prompt, temperature=0.3)
        raw_questions = response_json.get("questions", [])
        if not isinstance(raw_questions, list):
            raw_questions = []

        sanitized_questions = []
        for idx, q in enumerate(raw_questions):
            q_text = (q.get("question") or "").strip()
            if not q_text:
                continue

            q_opts = q.get("options")
            if isinstance(q_opts, list):
                clean_opts = [str(opt).strip() for opt in q_opts if str(opt).strip()]
            elif isinstance(q_opts, dict):
                clean_opts = [f"{k}) {v}" for k, v in q_opts.items()]
            else:
                clean_opts = []

            # Normalize correct_answer
            corr = str(q.get("correct_answer") or "").strip()
            if clean_opts and corr:
                # If correct_answer is just "A", "B", etc. or match with prefix
                match_prefix = re.match(r"^([A-D])[\)\.\:\s]", corr, re.IGNORECASE)
                if match_prefix:
                    corr = match_prefix.group(1).upper()

            sanitized_questions.append({
                "id": f"gen_{idx + 1}",
                "question": q_text,
                "type": q.get("type") or question_type or "MCQ",
                "difficulty": q.get("difficulty") or difficulty or "medium",
                "marks": int(q.get("marks") or 1),
                "options": clean_opts,
                "correct_answer": corr or (clean_opts[0] if clean_opts else "A"),
                "explanation": (q.get("explanation") or "Derived from uploaded curriculum document.").strip(),
                "topic_suggested": q.get("topic_suggested") or meta.get("subject") or "General",
            })

        return sanitized_questions

    except Exception as e:
        logger.error(f"Failed to generate questions from document {document_id}: {e}", exc_info=True)
        raise
