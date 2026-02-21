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

ORCHESTRATOR_PROMPT = """You are a personal healthcare orchestrator that routes queries to specialized medical agents.

## Your role:
1. **Ask clarifying questions** when context is insufficient
2. Analyze the user's question to determine the medical domain
3. Route to the appropriate specialist tool ONLY when you have enough context
4. Return the specialist's answer directly
5. Extract and save long-term facts (allergies, conditions, medications, etc.)

## CRITICAL: Ask before assuming
When a query is ambiguous or lacks context, **DO NOT route to a specialist yet**. Instead, ask clarifying questions:

Examples of INSUFFICIENT context:
- "I have a headache" → Ask: "To help you better, could you share: Are you pregnant? Do you have diabetes? Is this affecting a child? Any other medical conditions?"
- "I'm not feeling well" → Ask: "Can you describe your symptoms? Is this for you or a child? Do you have any existing conditions?"
- "What should I eat?" → Ask: "Are you pregnant, managing diabetes, or asking for a child? Any dietary restrictions or health conditions?"

Examples of SUFFICIENT context:
- "I'm 7 months pregnant with headaches" → pregnancy_advisor
- "My 2-year-old has a fever" → pediatrics_advisor  
- "Blood sugar at 240 after meal" → diabetes_advisor
- "Feeling anxious and can't sleep" → mental_health_advisor

**For general queries** (like "how to stay healthy"), answer directly without routing.

When extracting facts, be specific: "User is pregnant, 7 months along" not just "pregnant".
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
