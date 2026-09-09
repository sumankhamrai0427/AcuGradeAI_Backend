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


def _extract_opt_letter(val: str) -> str:
    s = (val or "").strip()
    m = re.match(r"^(?:option\s+)?\(?([A-Da-d])(?:\)|\.|\:|\-|\s|$)", s, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return ""


def evaluate_question(question: Question, student_answer: str) -> dict:
    student_ans = (student_answer or "").strip()
    correct_ans = (question.correct_answer or "").strip()
    is_correct = False

    if question.type in ("mcq", "logical"):
        student_letter = _extract_opt_letter(student_ans)
        correct_letter = _extract_opt_letter(correct_ans)

        # 1. Direct letter equality (e.g. "A" == "A")
        if student_letter and correct_letter and student_letter == correct_letter:
            is_correct = True

        # 2. Match against options array
        if not is_correct and question.options:
            student_matched_letter = student_letter
            correct_matched_letter = correct_letter

            for idx, opt in enumerate(question.options):
                opt_str = str(opt).strip()
                opt_let = _extract_opt_letter(opt_str) or chr(65 + idx)
                opt_body = re.sub(r"^(?:option\s+)?\(?[A-Da-d]\)?[\).\:\-]?\s*", "", opt_str, flags=re.IGNORECASE).strip().lower()

                if not student_matched_letter:
                    if student_ans.lower() == opt_body or student_ans.lower() == opt_str.lower():
                        student_matched_letter = opt_let

                if not correct_matched_letter:
                    if (
                        correct_ans.lower() == opt_body
                        or correct_ans.lower() == opt_str.lower()
                        or (len(correct_ans) > 3 and correct_ans.lower() in opt_body)
                        or (len(correct_ans) > 3 and opt_body in correct_ans.lower())
                    ):
                        correct_matched_letter = opt_let

            if student_matched_letter and correct_matched_letter and student_matched_letter == correct_matched_letter:
                is_correct = True

        # 3. Direct text equality
        if not is_correct:
            clean_s = re.sub(r"^(?:option\s+)?\(?[A-Da-d]\)?[\).\:\-]?\s*", "", student_ans, flags=re.IGNORECASE).strip().lower()
            clean_c = re.sub(r"^(?:option\s+)?\(?[A-Da-d]\)?[\).\:\-]?\s*", "", correct_ans, flags=re.IGNORECASE).strip().lower()
            if clean_s and clean_s == clean_c:
                is_correct = True

    elif question.type == "numerical":
        num_student = _to_float(student_ans)
        num_correct = _to_float(correct_ans)
        if num_student is not None and num_correct is not None:
            is_correct = abs(num_student - num_correct) < 0.05
        else:
            is_correct = student_ans.lower() == correct_ans.lower()
    else:  # objective / saq
        clean_s = student_ans.lower().strip()
        clean_c = correct_ans.lower().strip()
        is_correct = bool(clean_s) and (clean_s in clean_c or clean_c in clean_s or clean_s == clean_c)

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
