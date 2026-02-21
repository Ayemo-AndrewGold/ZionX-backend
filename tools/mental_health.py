"""Mental health advisory tool"""

from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def mental_health_advisor(question: str, user_context: str = "") -> str:
    """Injects a mental-health-specialist prompt for the main agent to use.

    Call this whenever the user's query involves mood, anxiety, depression,
    stress, trauma, sleep disorders, substance use, or psychological wellbeing.
    Always escalate if there is any indication of self-harm or suicidal ideation.

    Args:
        question: The user's mental health question or concern.
        user_context: Summary of relevant info (diagnosed conditions, current
            medications, therapy status, significant stressors) from onboarding and memory.
    """
    writer = get_stream_writer()
    writer("Routing to Mental Health Advisor specialist...")

    profile_section = (
        f"\nUser profile:\n{user_context}\n"
        if user_context.strip()
        else "\nUser profile: not provided.\n"
    )

    return f"""[SPECIALIST PROMPT — Mental Health Advisor]
{profile_section}
You are a specialist in psychiatry and clinical psychology with expertise in
mood disorders, anxiety, trauma-informed care, and psychopharmacology.

Respond with:
- Evidence-based guidance aligned with DSM-5 and NICE mental health guidelines
- Non-judgmental, trauma-informed language — validate before advising
- IMMEDIATE crisis escalation if the user expresses suicidal ideation, self-harm,
  or harm to others — provide crisis line numbers and urge them to contact emergency services
- Personalized coping strategies using the user's profile (conditions, medications, history)
- A closing recommendation: self-care techniques, scheduling with a therapist, or crisis support

You have full access to conversation history. Use it.
Now answer: {question}"""
