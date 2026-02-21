"""Orchestrator agent"""

from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from tools import ALL_TOOLS
from agent_config import AgentConfig

load_dotenv()

ORCHESTRATOR_PROMPT = """You are a personal healthcare assistant with access to four specialist tools.

## Specialist tools — call the right one based on the query, unless you can answer them on your own

When you learn a long-term fact about the user (allergy, condition, preference, etc.), populate the `fact` field. Otherwise leave it null.
"""


class Chat(BaseModel):
    normal_response: str = Field(description="Answer to the user's query")
    fact: str | None = Field(default=None, description="Long-term fact about the user extracted from this message, if any")


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
