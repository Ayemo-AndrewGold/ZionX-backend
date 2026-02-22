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

When user query is a greeting or pleasantry, be concise.

## Core Rules:
1. **Ask clarifying questions** when context is insufficient - don't assume medical domains
2. Route to specialist tools ONLY with clear context
3. Answer general health queries directly without routing
4. Extract specific long-term facts (conditions, medications, allergies, etc.)
5. **Assess risk and urgency** for medical queries - set risk_level and urgency fields

## When to Ask vs Route:
**INSUFFICIENT context** - Ask questions first:
- "I have a headache" → Ask clarifying questions
- "I'm not feeling well" → Ask for symptoms, who it's for, existing conditions

**SUFFICIENT context** - Route immediately:
- "I'm 7 months pregnant with headaches" → pregnancy_advisor
- "My 2-year-old has a fever" → pediatrics_advisor
- "Blood sugar at 240 after meal" → diabetes_advisor
- "Feeling anxious and can't sleep" → mental_health_advisor
- "Chest pain and shortness of breath" → emergency_triage
- "What patterns do you see in my health?" → preventive_health_analyzer

## Risk Assessment:
**Set risk_level and urgency for medical queries:**
- **critical** + **call_emergency**: Life-threatening symptoms (chest pain, severe bleeding, stroke signs, difficulty breathing, altered consciousness)
- **high** + **seek_urgent_care**: Severe symptoms needing immediate attention (high fever in infant, severe pain, suspected fracture)
- **medium** + **schedule_visit**: Concerning symptoms needing professional evaluation (persistent symptoms, worsening patterns)
- **low** + **monitor**: Mild symptoms safe to self-monitor with clear red flags to watch

Be specific when extracting facts: "User is pregnant, 7 months along" not just "pregnant".
"""


class Chat(BaseModel):
    normal_response: str = Field(description="Answer to the user's query")
    fact: str | None = Field(default=None, description="Long-term fact about the user extracted from this message, if any")
    risk_level: str | None = Field(default=None, description="Risk assessment: 'low', 'medium', 'high', or 'critical' - only set when medical context warrants it")
    urgency: str | None = Field(default=None, description="Recommended action: 'monitor', 'schedule_visit', 'seek_urgent_care', or 'call_emergency' - only set when medical context warrants it")


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
