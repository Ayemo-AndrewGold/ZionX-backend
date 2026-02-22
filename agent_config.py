"""Configuration for ZionX agent orchestration.

LLM model and temperature come from core.config (single source of truth).
Only the context-editing middleware parameters live here.
"""
import os
from dataclasses import dataclass

from core.config import MODEL_NAME, TEMPERATURE


@dataclass
class AgentConfig:
    """Agent behaviour parameters — all fields overridable via env vars."""

    model_name: str = MODEL_NAME
    temperature: float = TEMPERATURE

    # Context-editing middleware
    context_editing_trigger_tokens: int = 50_000
    context_editing_keep_calls: int = 4

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            context_editing_trigger_tokens=int(
                os.getenv("CONTEXT_EDITING_TRIGGER_TOKENS", 50_000)
            ),
            context_editing_keep_calls=int(
                os.getenv("CONTEXT_EDITING_KEEP_CALLS", 4)
            ),
        )
