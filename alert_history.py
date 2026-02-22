"""Emergency alert history tracking system."""

import json
from pathlib import Path
from datetime import datetime

ALERTS_DIR = "emergency_alerts_history"


def _ensure_alerts_dir():
    """Ensure the alerts directory exists."""
    Path(ALERTS_DIR).mkdir(exist_ok=True)


def save_alert_record(user_id: str, alert_data: dict, success: bool, message: str) -> dict:
    """Record an emergency alert attempt.
    
    Args:
        user_id: User identifier
        alert_data: Dict with alert details (severity, symptoms, etc.)
        success: Whether the alert was sent successfully
        message: Result message
    
    Returns:
        dict with saved alert record
    """
    _ensure_alerts_dir()
    
    # Load existing alerts
    alerts = load_alert_history(user_id)
    
    # Create new alert record
    alert_record = {
        "alert_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "severity": alert_data.get("severity"),
        "symptoms": alert_data.get("symptoms", ""),
        "ai_assessment": alert_data.get("ai_assessment", ""),
        "user_location": alert_data.get("user_location", "Not provided"),
        "success": success,
        "message": message
    }
    
    alerts.append(alert_record)
    
    # Save to file
    path = Path(ALERTS_DIR) / f"{user_id}.json"
    try:
        with path.open("w") as f:
            json.dump(alerts, f, indent=2)
        return alert_record
    except Exception as e:
        print(f"Error saving alert record for {user_id}: {e}")
        return {}


def load_alert_history(user_id: str, days: int = None) -> list:
    """Load emergency alert history for a user.
    
    Args:
        user_id: User identifier
        days: Number of recent days to retrieve (None = all)
    
    Returns:
        List of alert records
    """
    _ensure_alerts_dir()
    path = Path(ALERTS_DIR) / f"{user_id}.json"
    
    try:
        if not path.exists():
            return []
        
        with path.open() as f:
            alerts = json.load(f)
        
        # Filter by days if specified
        if days:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            alerts = [
                a for a in alerts 
                if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff
            ]
        
        return alerts
    except Exception as e:
        print(f"Error loading alert history for {user_id}: {e}")
        return []


def get_alerts_summary(user_id: str, days: int = 30) -> dict:
    """Get a summary of emergency alerts for display.
    
    Returns:
        Dict with alert statistics
    """
    alerts = load_alert_history(user_id, days=days)
    
    if not alerts:
        return {
            "total_alerts": 0,
            "successful_alerts": 0,
            "failed_alerts": 0,
            "latest_alert": None,
            "recent_alerts": []
        }
    
    successful = [a for a in alerts if a.get("success")]
    failed = [a for a in alerts if not a.get("success")]
    
    # Get recent alerts
    recent_alerts = sorted(
        alerts,
        key=lambda x: x["timestamp"],
        reverse=True
    )[:10]  # Last 10 alerts
    
    return {
        "total_alerts": len(alerts),
        "successful_alerts": len(successful),
        "failed_alerts": len(failed),
        "latest_alert": alerts[-1] if alerts else None,
        "recent_alerts": recent_alerts,
        "days_monitored": days
    }
