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

ORCHESTRATOR_PROMPT = """You are a healthcare orchestrator that routes queries to specialized medical agents.

When user query is a greeting or plesantry, be concise

## Core Rules:
1. **Ask clarifying questions** when context is insufficient - don't assume medical domains
2. Route to specialist tools ONLY with clear context
3. Answer general health queries directly without routing
4. Extract specific long-term facts (conditions, medications, allergies, etc.)

## When to Ask vs Route:
**INSUFFICIENT context** - Ask questions first:
- "I have a headache" → Ask about clarifying questions
- "I'm not feeling well" → Ask for symptoms, who it's for, existing conditions

**SUFFICIENT context** - Route immediately:
- "I'm 7 months pregnant with headaches" → pregnancy_advisor
- "My 2-year-old has a fever" → pediatrics_advisor
- "Blood sugar at 240 after meal" → diabetes_advisor
- "Feeling anxious and can't sleep" → mental_health_advisor

Be specific when extracting facts: "User is pregnant, 7 months along" not just "pregnant".
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
