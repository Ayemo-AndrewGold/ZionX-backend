"""Pydantic schemas shared across the application."""
from pydantic import BaseModel, Field


class Chat(BaseModel):
    normal_response: str = Field(description="Answer to the user's query")
    fact: str | None = Field(
        default=None,
        description="Long-term fact about the user extracted from this message, if any",
    )
    risk_level: str | None = Field(
        default=None,
        description="Risk assessment: 'low', 'medium', 'high', or 'critical' — only set when medical context warrants it",
    )
    urgency: str | None = Field(
        default=None,
        description="Recommended action: 'monitor', 'schedule_visit', 'seek_urgent_care', or 'call_emergency' — only set when medical context warrants it",
    )
