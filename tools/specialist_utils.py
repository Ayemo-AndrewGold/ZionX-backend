"""Shared utilities for specialist LLM instances.

Provides a properly-keyed cache (specialist type + model + temperature) and a
`build_messages` helper that every tool uses to build its message list,
eliminating repeated boilerplate across tool files.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from core.config import MODEL_NAME, SPECIALIST_TEMPERATURE

load_dotenv()

# Cache keyed on (specialist_type, model, temperature) so that tools that
# override temperature (e.g. emergency_triage) always receive the correct
# instance rather than the first one that was cached.
_cache: dict[tuple, ChatGoogleGenerativeAI] = {}


def get_specialist(
    specialist_type: str = "default",
    model: str | None = None,
    temperature: float | None = None,
) -> ChatGoogleGenerativeAI:
    """Return a cached ChatGoogleGenerativeAI instance for the given specialist."""
    model = model or MODEL_NAME
    temperature = temperature if temperature is not None else SPECIALIST_TEMPERATURE
    key = (specialist_type, model, temperature)
    if key not in _cache:
        _cache[key] = ChatGoogleGenerativeAI(model=model, temperature=temperature)
    return _cache[key]


def build_messages(system_prompt: str, question: str, user_context: str = "") -> list[dict]:
    """Build the message list for a specialist LLM call.

    Appends the user context block to the system prompt when provided,
    keeping each tool's call site to a single line.
    """
    system = system_prompt
    if user_context.strip():
        system = f"{system_prompt}\n\nUser Context:\n{user_context}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
