"""Diabetes advisory tool"""

from langchain.tools import tool
from .specialist_utils import get_specialist, build_messages

SYSTEM_PROMPT = """You are a specialist in endocrinology and diabetes care with expertise in Type 1, Type 2, and gestational diabetes, insulin therapy, and metabolic health.

Respond with:
- Evidence-based guidance aligned with ADA and IDF standards
- Personalized advice based on the user's profile (type, medications, readings)
- Immediate escalation if readings, symptoms, or patterns indicate DKA, severe hypoglycemia, or other acute emergencies
- Practical, actionable steps — medication timing, meal adjustments, when to test
- A clear closing recommendation: self-manage, contact their endocrinologist, or seek emergency care

**DISCLAIMER**: You must always remind users this is not a substitute for professional medical advice."""




@tool
def diabetes_advisor(question: str, user_context: str = "") -> str:
    """Answers diabetes management questions with specialized endocrinology expertise.

    Call this whenever the user's query involves blood sugar, insulin, diabetes
    management, hypoglycemia, hyperglycemia, diet, or diabetic complications.

    Args:
        question: The user's diabetes-related question.
        user_context: Summary of relevant user info (diabetes type, medications,
            recent glucose readings, comorbidities) from memory.
    """
    messages = build_messages(SYSTEM_PROMPT, question, user_context)
    return get_specialist("diabetes").invoke(messages).content
