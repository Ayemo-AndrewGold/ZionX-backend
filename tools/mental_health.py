"""Mental health advisory tool"""

from langchain.tools import tool
from .specialist_utils import get_specialist, build_messages

SYSTEM_PROMPT = """You are a specialist in psychiatry and clinical psychology with expertise in mood disorders, anxiety, trauma-informed care, and psychopharmacology.

Respond with:
- Evidence-based guidance aligned with DSM-5 and NICE mental health guidelines
- Non-judgmental, trauma-informed language — validate before advising
- IMMEDIATE crisis escalation if the user expresses suicidal ideation, self-harm, or harm to others — provide crisis line numbers and urge them to contact emergency services
- Personalized coping strategies using the user's profile (conditions, medications, history)
- A closing recommendation: self-care techniques, scheduling with a therapist, or crisis support

**DISCLAIMER**: You must always remind users this is not a substitute for professional medical advice."""




@tool
def mental_health_advisor(question: str, user_context: str = "") -> str:
    """Answers mental health questions with specialized psychiatric expertise.

    Call this whenever the user's query involves mood, anxiety, depression,
    stress, trauma, sleep disorders, substance use, or psychological wellbeing.
    Always escalate if there is any indication of self-harm or suicidal ideation.

    Args:
        question: The user's mental health question or concern.
        user_context: Summary of relevant info (diagnosed conditions, current
            medications, therapy status, significant stressors) from memory.
    """
    messages = build_messages(SYSTEM_PROMPT, question, user_context)
    return get_specialist("mental_health").invoke(messages).content
