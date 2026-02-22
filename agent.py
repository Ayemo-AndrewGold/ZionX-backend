"""Orchestrator agent factory."""

from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from tools import ALL_TOOLS
from agent_config import AgentConfig
from core.models import Chat  # noqa: F401 — re-exported for backwards compat
from prompts import ORCHESTRATOR_PROMPT

load_dotenv()


def create_zionx_agent(config: AgentConfig | None = None):
    """orchestrator agent"""
    if config is None:
        config = AgentConfig.from_env()

    model = ChatGoogleGenerativeAI(
        model=config.model_name,
        temperature=config.temperature,
    )

    middleware = [
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=config.context_editing_trigger_tokens,
                    keep=config.context_editing_keep_calls,
                )
            ],
        )
    ]

    return create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=ORCHESTRATOR_PROMPT,
        checkpointer=MemorySaver(),
        middleware=middleware,
        response_format=Chat,
    )
