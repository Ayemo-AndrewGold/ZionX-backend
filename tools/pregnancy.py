"""Pregnant woman advisory tool"""

from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def pregnancy_advisor(question: str, user_context: str = "") -> str:
    """Injects a pregnancy-specialist prompt for the main agent to use when answering.

    Call this tool whenever the user's query relates to pregnancy — symptoms,
    nutrition, exercise, emotional wellbeing, fetal development, or labor prep.
    The main agent will use the returned instructions, combined with its existing
    conversation history and memory, to produce a clinically appropriate response.

    Args:
        question: The user's pregnancy-related question or concern.
        user_context: Optional. A summary of relevant user info (allergies, medications,
            known conditions, trimester) composed by the main agent from onboarding
            data and long-term memory. Leave empty if no profile data is available.
    """
    writer = get_stream_writer()
    writer("Routing to Pregnancy Advisor specialist...")

    profile_section = (
        f"\nUser medical profile:\n{user_context}\n"
        if user_context.strip()
        else "\nUser medical profile: not provided.\n"
    )

    return f"""[SPECIALIST PROMPT — Pregnancy Advisor]
{profile_section}
You are a specialized pregnancy healthcare advisor with deep expertise in
obstetrics, maternal nutrition, fetal development, and perinatal mental health.

Respond with:
- Clinical accuracy aligned with ACOG and WHO maternal guidelines
- Specificity — use the user's profile above to personalize your answer
- Safety priority — immediately flag any symptom that warrants urgent care
- Empathy — acknowledge the emotional weight of pregnancy without dismissing risks
- A clear closing recommendation: whether to self-monitor, contact their midwife,
  or seek emergency care

You still have full access to the conversation history. Use it.
Now answer the user's question: {question}"""
