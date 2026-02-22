"""Tool registry — import all tools here and add to ALL_TOOLS.

To add a new tool:
  1. Create tools/<your_tool>.py and decorate with @tool
  2. Import it below and append to ALL_TOOLS and __all__
"""

from tools.pregnancy import pregnancy_advisor
from tools.diabetes import diabetes_advisor
from tools.pediatrics import pediatrics_advisor
from tools.mental_health import mental_health_advisor
from tools.emergency import emergency_triage
from tools.preventive import preventive_health_analyzer

# ── Registry ──────────────────────────────────────────────────────────────────
ALL_TOOLS = [
    emergency_triage,
    pregnancy_advisor,
    diabetes_advisor,
    pediatrics_advisor,
    mental_health_advisor,
    preventive_health_analyzer,
    # add new tools here ↓
]

__all__ = [
    "pregnancy_advisor",
    "diabetes_advisor",
    "pediatrics_advisor",
    "mental_health_advisor",
    "emergency_triage",
    "preventive_health_analyzer",
    # add new tool names here ↓
    "ALL_TOOLS",
]
