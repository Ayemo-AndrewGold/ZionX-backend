"""Diabetes advisory tool"""

from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def diabetes_advisor(question: str, user_context: str = "") -> str:
    """Injects a diabetes-specialist prompt for the main agent to use.

    Call this whenever the user's query involves blood sugar, insulin, diabetes
    management, hypoglycemia, hyperglycemia, diet, or diabetic complications.

    Args:
        question: The user's diabetes-related question.
        user_context: Summary of relevant user info (diabetes type, medications,
            recent glucose readings, comorbidities) from onboarding and memory.
    """
    writer = get_stream_writer()
    writer("Routing to Diabetes Advisor specialist...")

    profile_section = (
        f"\nUser medical profile:\n{user_context}\n"
        if user_context.strip()
        else "\nUser medical profile: not provided.\n"
    )

    return f"""[SPECIALIST PROMPT — Diabetes Advisor]
{profile_section}
You are a specialist in endocrinology and diabetes care with expertise in
Type 1, Type 2, and gestational diabetes, insulin therapy, and metabolic health.

Respond with:
- Evidence-based guidance aligned with ADA and IDF standards
- Personalized advice based on the user's profile (type, medications, readings)
- Immediate escalation if readings, symptoms, or patterns indicate DKA, severe
  hypoglycemia, or other acute emergencies
- Practical, actionable steps — medication timing, meal adjustments, when to test
- A clear closing recommendation: self-manage, contact their endocrinologist, or seek emergency care

You have full access to conversation history. Use it.
Now answer: {question}"""
