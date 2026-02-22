"""Daily health tracking system for storing and analyzing user updates."""

import json
from pathlib import Path
from datetime import datetime

TRACKING_DIR = "tracking"


def _ensure_tracking_dir():
    """Ensure the tracking directory exists."""
    Path(TRACKING_DIR).mkdir(exist_ok=True)


def save_daily_tracking(user_id: str, tracking_data: dict) -> dict:
    """Save a daily tracking entry for a user.
    
    Args:
        user_id: User identifier
        tracking_data: Dict with keys like 'mood', 'symptoms', 'energy', 'medications', 'notes'
    
    Returns:
        dict with saved entry including timestamp and entry_id
    """
    _ensure_tracking_dir()
    
    # Load existing entries
    entries = load_tracking_history(user_id)
    
    # Create new entry
    entry = {
        "entry_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        **tracking_data
    }
    
    entries.append(entry)
    
    # Save to file
    path = Path(TRACKING_DIR) / f"{user_id}.json"
    try:
        with path.open("w") as f:
            json.dump(entries, f, indent=2)
        return entry
    except Exception as e:
        print(f"Error saving tracking data for {user_id}: {e}")
        return {}


def load_tracking_history(user_id: str, days: int = None) -> list:
    """Load tracking history for a user.
    
    Args:
        user_id: User identifier
        days: Number of recent days to retrieve (None = all)
    
    Returns:
        List of tracking entries
    """
    _ensure_tracking_dir()
    path = Path(TRACKING_DIR) / f"{user_id}.json"
    
    try:
        if not path.exists():
            return []
        
        with path.open() as f:
            entries = json.load(f)
        
        # Filter by days if specified
        if days:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            entries = [
                e for e in entries 
                if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff
            ]
        
        return entries
    except Exception as e:
        print(f"Error loading tracking history for {user_id}: {e}")
        return []


def get_tracking_summary(user_id: str, days: int = 7) -> str:
    """Get a formatted summary of recent tracking data for AI context.
    
    Returns:
        Formatted string summarizing recent entries
    """
    entries = load_tracking_history(user_id, days=days)
    
    if not entries:
        return ""
    
    summary_parts = [f"Recent {days}-day health tracking:"]
    
    for entry in entries[-10:]:  # Last 10 entries
        date = entry.get("date", "Unknown date")
        parts = [f"- {date}:"]
        
        if "mood" in entry:
            parts.append(f"Mood: {entry['mood']}")
        if "energy" in entry:
            parts.append(f"Energy: {entry['energy']}")
        if "symptoms" in entry and entry["symptoms"]:
            parts.append(f"Symptoms: {', '.join(entry['symptoms'])}")
        if "medications" in entry and entry["medications"]:
            parts.append(f"Medications: {', '.join(entry['medications'])}")
        if "notes" in entry and entry["notes"]:
            parts.append(f"Notes: {entry['notes']}")
        
        summary_parts.append(" | ".join(parts))
    
    return "\n".join(summary_parts)
