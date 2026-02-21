"""Pregnant woman advisory tool"""

from langchain.tools import tool
from .specialist_utils import get_specialist

SYSTEM_PROMPT = """You are a specialized pregnancy healthcare advisor with deep expertise in obstetrics, maternal nutrition, fetal development, and perinatal mental health.

Respond with:
- Clinical accuracy aligned with ACOG and WHO maternal guidelines
- Specificity — use the user's profile to personalize your answer
- Safety priority — immediately flag any symptom that warrants urgent care
- Empathy — acknowledge the emotional weight of pregnancy without dismissing risks
- A clear closing recommendation: whether to self-monitor, contact their midwife, or seek emergency care

**DISCLAIMER**: You must always remind users this is not a substitute for professional medical advice."""




@tool
def pregnancy_advisor(question: str, user_context: str = "") -> str:
    """Answers pregnancy-related questions with specialized obstetric expertise.

    Call this tool whenever the user's query relates to pregnancy — symptoms,
    nutrition, exercise, emotional wellbeing, fetal development, or labor prep.

    Args:
        question: The user's pregnancy-related question or concern.
        user_context: Optional. Relevant user info (allergies, medications,
            known conditions, trimester) from memory.
    """
    profile = f"\n\nUser Profile:\n{user_context}" if user_context.strip() else ""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + profile},
        {"role": "user", "content": question}
    ]
    
    response = get_specialist("pregnancy", temperature=0.1).invoke(messages)
    return response.content
