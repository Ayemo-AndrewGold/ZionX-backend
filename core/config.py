"""Single source of truth for LLM model configuration.

All other modules import from here instead of reading env vars directly.
"""
import os

MODEL_NAME: str = os.getenv("AGENT_MODEL_NAME", "gemini-3-flash-preview")
TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
SPECIALIST_TEMPERATURE: float = float(os.getenv("SPECIALIST_TEMPERATURE", "0.1"))
