from model.mistral_client import call_llm_chat
from helper.rag_engine import retrieve_document_context


def generate_chat_response(messages: list, student_context: dict = None) -> str:
    """
    Generate a chat response focusing on pedagogical and academic support for parents/students.
    Uses ChromaDB RAG for curriculum grounding and student mastery metrics when available.
    """
    context_str = ""
    rag_snippets = []

    last_user_query = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_query = msg.get("content", "")
            break

    if student_context:
        name = student_context.get("name", "the student")
        grade = student_context.get("classGrade", "their class")
        board = student_context.get("targetBoard", "their board")
        weak_topics = student_context.get("weakTopics", [])
        avg_score = student_context.get("averageScore", None)
        recent_scores = student_context.get("recentScores", [])

        perf_summary = []
        if avg_score is not None:
            perf_summary.append(f"Average score: {avg_score}%")
        if weak_topics:
            perf_summary.append(f"Needs attention on: {', '.join(weak_topics[:3])}")
        if recent_scores:
            perf_summary.append(f"Recent exam scores: {', '.join(map(str, recent_scores[:3]))}")

        context_str = (
            f"You are assisting regarding student '{name}' in {grade} ({board}). "
            f"{' | '.join(perf_summary) if perf_summary else ''}\n"
        )

        # Semantic RAG retrieval over ChromaDB for academic questions
        if last_user_query:
            try:
                rag_snippets = retrieve_document_context(
                    board=board,
                    class_grade=grade,
                    subject="Mathematics",
                    query_text=last_user_query,
                    top_k=2
                )
            except Exception:
                rag_snippets = []
    else:
        context_str = "You are assisting a user on the SahajPath adaptive learning platform.\n"

    rag_text = ""
    if rag_snippets:
        rag_text = f"\nVERIFIED CURRICULUM CONTEXT (ground your answers on this):\n" + "\n---\n".join(rag_snippets) + "\n"

    system_prompt = f"""You are SahajPath Teacher Support, a warm, empathetic, and knowledgeable educational assistant.
{context_str}{rag_text}
CORE GUIDELINES:
1. **Brevity & Simplicity**: Keep answers conversational, friendly, and practical (2 to 4 concise sentences).
2. **Pedagogical Support**: Encourage positive study habits, play-based learning for primary kids, and structured problem-solving for seniors.
3. **Curriculum Grounding**: When explaining academic concepts, use simple everyday examples grounded in the textbook curriculum.
4. **Guardrails**: Only answer education, learning, parenting, and syllabus-related queries.

Keep your response under 70 words whenever possible."""

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        if msg.get("role") in ["user", "assistant"]:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    response_text = call_llm_chat(formatted_messages, json_mode=False, temperature=0.5)
    return response_text

