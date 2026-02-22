"""Risk monitoring system for tracking health risk assessments."""

import json
from pathlib import Path
from datetime import datetime

RISK_DIR = "risk_assessments"


def _ensure_risk_dir():
    """Ensure the risk assessments directory exists."""
    Path(RISK_DIR).mkdir(exist_ok=True)


def save_risk_assessment(user_id: str, risk_data: dict) -> dict:
    """Save a risk assessment from a chat interaction.
    
    Args:
        user_id: User identifier
        risk_data: Dict with 'risk_level', 'urgency', 'message', 'ai_response'
    
    Returns:
        dict with saved assessment including timestamp
    """
    _ensure_risk_dir()
    
    # Load existing assessments
    assessments = load_risk_history(user_id)
    
    # Create new assessment
    assessment = {
        "assessment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "risk_level": risk_data.get("risk_level"),
        "urgency": risk_data.get("urgency"),
        "user_message": risk_data.get("message", ""),
        "ai_response": risk_data.get("ai_response", ""),
        "emergency_alert_sent": risk_data.get("emergency_alert_sent", False)
    }
    
    assessments.append(assessment)
    
    # Save to file
    path = Path(RISK_DIR) / f"{user_id}.json"
    try:
        with path.open("w") as f:
            json.dump(assessments, f, indent=2)
        return assessment
    except Exception as e:
        print(f"Error saving risk assessment for {user_id}: {e}")
        return {}


def load_risk_history(user_id: str, days: int = None) -> list:
    """Load risk assessment history for a user.
    
    Args:
        user_id: User identifier
        days: Number of recent days to retrieve (None = all)
    
    Returns:
        List of risk assessments
    """
    _ensure_risk_dir()
    path = Path(RISK_DIR) / f"{user_id}.json"
    
    try:
        if not path.exists():
            return []
        
        with path.open() as f:
            assessments = json.load(f)
        
        # Filter by days if specified
        if days:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            assessments = [
                a for a in assessments 
                if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff
            ]
        
        return assessments
    except Exception as e:
        print(f"Error loading risk history for {user_id}: {e}")
        return []


def get_risk_summary(user_id: str, days: int = 30) -> dict:
    """Get a summary of risk assessments for display.
    
    Returns:
        Dict with risk statistics and recent high-risk events
    """
    assessments = load_risk_history(user_id, days=days)
    
    if not assessments:
        return {
            "total_assessments": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "latest_assessment": None,
            "high_risk_events": []
        }
    
    # Count risk levels
    high_risk = [a for a in assessments if a.get("risk_level") == "high"]
    medium_risk = [a for a in assessments if a.get("risk_level") == "medium"]
    low_risk = [a for a in assessments if a.get("risk_level") == "low"]
    
    # Get recent high-risk events
    high_risk_events = sorted(
        high_risk,
        key=lambda x: x["timestamp"],
        reverse=True
    )[:5]  # Last 5 high-risk events
    
    return {
        "total_assessments": len(assessments),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "low_risk_count": len(low_risk),
        "latest_assessment": assessments[-1] if assessments else None,
        "high_risk_events": high_risk_events,
        "days_monitored": days
    }
