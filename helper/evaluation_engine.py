"""Per-question evaluation logic, ported from the frontend's original
server.ts /api/evaluate-exam handler (MCQ/logical letter matching, numerical
tolerance, objective substring matching)."""
import re

from model.models import Question


def _identify_misconception(question: Question, student_answer: str) -> str | None:
    if not student_answer:
        return "Question skipped / incomplete attempt under time pressure."
    if question.type == "numerical":
        return "Calculation step error or unit conversion discrepancy."
    if question.type == "logical":
        return "Assertion-Reasoning logical causal link was misinterpreted."
    return "Conceptual distinction between related syllabus definitions."


def evaluate_question(question: Question, student_answer: str) -> dict:
    student_ans = (student_answer or "").strip()
    correct_ans = (question.correct_answer or "").strip()
    is_correct = False

    if question.type in ("mcq", "logical"):
        student_letter = student_ans.upper()[:1] if student_ans else ""
        correct_letter = correct_ans.upper()[:1] if correct_ans else ""
        is_correct = student_letter == correct_letter or student_ans.lower() == correct_ans.lower()
    elif question.type == "numerical":
        num_student = _to_float(student_ans)
        num_correct = _to_float(correct_ans)
        if num_student is not None and num_correct is not None:
            is_correct = abs(num_student - num_correct) < 0.05
        else:
            is_correct = student_ans.lower() == correct_ans.lower()
    else:  # objective
        is_correct = (
            student_ans.lower() in correct_ans.lower() or correct_ans.lower() in student_ans.lower()
        ) and bool(student_ans)

    marks_awarded = question.marks if is_correct else 0

    return {
        "questionId": question.id,
        "questionNumber": question.question_number,
        "type": question.type,
        "questionText": question.question_text,
        "options": question.options,
        "studentAnswer": student_ans or "(Not Answered)",
        "correctAnswer": correct_ans,
        "isCorrect": is_correct,
        "marksAwarded": marks_awarded,
        "questionMarks": question.marks or 1,
        "explanation": question.explanation,
        "misconceptionIdentified": None if is_correct else _identify_misconception(question, student_ans),
        "referenceLinks": question.reference_links or [],
        "topic": question.topic,
    }


def _to_float(value: str) -> float | None:
    cleaned = re.sub(r"[^0-9.\-]", "", value or "")
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def evaluate_exam(questions: list[Question], answers: dict[str, str]) -> tuple[list[dict], int]:
    evaluations = []
    marks_obtained = 0
    for question in sorted(questions, key=lambda q: q.question_number):
        result = evaluate_question(question, answers.get(question.id, ""))
        evaluations.append(result)
        marks_obtained += result["marksAwarded"]
    return evaluations, marks_obtained
