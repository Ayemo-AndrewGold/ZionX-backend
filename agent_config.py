"""Configuration for ZionX agent orchestration."""
import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Agent behaviour and resource limits — all fields overridable via env vars."""

    model_name: str = "gemini-3-flash-preview"
    temperature: float = 0.1
    max_iterations: int = 25

    # Context-editing middleware
    context_editing_trigger_tokens: int = 50_000
    context_editing_keep_calls: int = 4

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            model_name=os.getenv("AGENT_MODEL_NAME", cls.model_name),
            temperature=float(os.getenv("AGENT_TEMPERATURE", cls.temperature)),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", cls.max_iterations)),
            context_editing_trigger_tokens=int(
                os.getenv("CONTEXT_EDITING_TRIGGER_TOKENS", cls.context_editing_trigger_tokens)
            ),
            context_editing_keep_calls=int(
                os.getenv("CONTEXT_EDITING_KEEP_CALLS", cls.context_editing_keep_calls)
            ),
        )
