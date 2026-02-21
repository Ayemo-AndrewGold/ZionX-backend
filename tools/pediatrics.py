"""Pediatrics advisory tool"""

from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def pediatrics_advisor(question: str, user_context: str = "") -> str:
    """Injects a pediatrics-specialist prompt for the main agent to use.

    Call this whenever the query concerns an infant, child, or adolescent —
    including development milestones, childhood illnesses, vaccinations,
    nutrition, behavior, or parental guidance.

    Args:
        question: The user's pediatric question or concern.
        user_context: Summary of relevant child info (age, weight, known conditions,
            vaccination history, current medications) from onboarding and memory.
    """
    writer = get_stream_writer()
    writer("Routing to Pediatrics Advisor specialist...")

    profile_section = (
        f"\nChild/patient profile:\n{user_context}\n"
        if user_context.strip()
        else "\nChild/patient profile: not provided.\n"
    )

    return f"""[SPECIALIST PROMPT — Pediatrics Advisor]
{profile_section}
You are a specialist pediatrician with expertise spanning neonatology, child
development, adolescent medicine, and preventive pediatric care.

Respond with:
- Guidance aligned with AAP and WHO pediatric standards
- Age-appropriate advice — dosages, milestones, and norms differ sharply by age
- Immediate red-flag escalation: high fever in neonates, respiratory distress,
  dehydration, altered consciousness, or any life-threatening presentation
- Clear, calm language that reassures caregivers while being medically precise
- A closing recommendation: monitor at home, schedule a pediatrician visit, or go to the ER

You have full access to conversation history. Use it.
Now answer: {question}"""
