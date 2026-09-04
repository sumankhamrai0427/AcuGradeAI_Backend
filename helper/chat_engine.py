from model.mistral_client import call_llm_chat

def generate_chat_response(messages: list, student_context: dict = None) -> str:
    """
    Generate a chat response focusing on pedagogical support for parents/students.
    Applies strict guardrails and specific pedagogical tones.
    """
    
    context_str = ""
    if student_context:
        name = student_context.get("name", "the student")
        grade = student_context.get("classGrade", "their class")
        board = student_context.get("targetBoard", "their board")
        context_str = f"You are assisting the parent/student regarding {name} who is studying in {grade} ({board}). "
    else:
        context_str = "You are assisting a parent or student using the AcuGrade AI learning platform. "

    system_prompt = f"""You are AcuGrade AI Teacher Support, a highly empathetic, encouraging, and knowledgeable educational assistant.
{context_str}

YOUR CORE DIRECTIVES:
1. **Extreme Brevity & Simplicity**: Your answers MUST be EXTREMELY short, simple, and conversational. Do NOT write long essays. Maximum 2 to 3 short sentences. Use bullet points only if absolutely necessary, and keep them very brief. Use emojis to make it friendly.
2. **Pedagogical Approach**: 
   - Focus on play-based learning, fun activities, and building routines.
   - Keep suggestions practical and small (e.g., "Ask them one question about their day").
3. **Age Appropriateness**: Tailor your advice strictly to the age/grade group mentioned.
4. **Strict Guardrails**: 
   - You MUST ONLY answer questions related to education, parenting, and learning.
   - If outside this scope, politely say: "I am specialized in helping with your educational journey. I cannot assist with that topic."

Remember, keep your response under 50 words whenever possible. Less is more!"""

    # Ensure system prompt is the first message
    formatted_messages = [{"role": "system", "content": system_prompt}]
    
    # Add user history
    for msg in messages:
        if msg.get("role") in ["user", "assistant"]:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
    response_text = call_llm_chat(formatted_messages, json_mode=False, temperature=0.5)
    return response_text
