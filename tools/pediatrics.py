"""Pediatrics advisory tool"""

from langchain.tools import tool
from .specialist_utils import get_specialist, build_messages

SYSTEM_PROMPT = """You are a specialist pediatrician with expertise spanning neonatology, child development, adolescent medicine, and preventive pediatric care.

Respond with:
- Guidance aligned with AAP and WHO pediatric standards
- Age-appropriate advice — dosages, milestones, and norms differ sharply by age
- Immediate red-flag escalation: high fever in neonates, respiratory distress, dehydration, altered consciousness, or any life-threatening presentation
- Clear, calm language that reassures caregivers while being medically precise
- A closing recommendation: monitor at home, schedule a pediatrician visit, or go to the ER

**DISCLAIMER**: You must always remind users this is not a substitute for professional medical advice."""




@tool
def pediatrics_advisor(question: str, user_context: str = "") -> str:
    """Answers pediatric questions with specialized child healthcare expertise.

    Call this whenever the query concerns an infant, child, or adolescent —
    including development milestones, childhood illnesses, vaccinations,
    nutrition, behavior, or parental guidance.

    Args:
        question: The user's pediatric question or concern.
        user_context: Summary of relevant child info (age, weight, known conditions,
            vaccination history, current medications) from memory.
    """
    messages = build_messages(SYSTEM_PROMPT, question, user_context)
    return get_specialist("pediatrics").invoke(messages).content
