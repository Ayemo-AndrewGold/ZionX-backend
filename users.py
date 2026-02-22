"""Simple file-based user authentication and management."""

import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta

USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    """Load users from the JSON file."""
    try:
        path = Path(USERS_FILE)
        if not path.exists():
            return {}
        with path.open() as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}


def _save_users(users: dict) -> None:
    """Save users to the JSON file."""
    try:
        with Path(USERS_FILE).open("w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")


def _load_sessions() -> dict:
    """Load active sessions from the JSON file."""
    try:
        path = Path(SESSIONS_FILE)
        if not path.exists():
            return {}
        with path.open() as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sessions: {e}")
        return {}


def _save_sessions(sessions: dict) -> None:
    """Save sessions to the JSON file."""
    try:
        with Path(SESSIONS_FILE).open("w") as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"Error saving sessions: {e}")


def register_user(username: str, password: str, email: str = None) -> tuple[bool, str]:
    """
    Register a new user.
    
    Returns:
        (success: bool, message: str)
    """
    if not username or not password:
        return False, "Username and password are required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    users = _load_users()
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password_hash": _hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "user_id": username,  # Use username as user_id for simplicity
        "profile": {
            "onboarding_complete": False,
            "medical_data": {
                "allergies": [],
                "medications_to_avoid": [],
                "blood_group": None,
                "conditions": [],
                "ongoing_issues": []
            },
            "emergency_contacts": {
                "consent_given": False,
                "doctor": {"name": None, "email": None, "phone": None},
                "loved_ones": []
            },
            "preferences": {
                "language": "en",
                "output_mode": "text"
            }
        }
    }
    
    _save_users(users)
    return True, "User registered successfully"


def login_user(username: str, password: str) -> tuple[bool, str, dict]:
    """
    Authenticate a user and create a session.
    
    Returns:
        (success: bool, message: str, user_data: dict)
    """
    if not username or not password:
        return False, "Username and password are required", {}
    
    users = _load_users()
    
    if username not in users:
        return False, "Invalid username or password", {}
    
    user = users[username]
    password_hash = _hash_password(password)
    
    if user["password_hash"] != password_hash:
        return False, "Invalid username or password", {}
    
    # Create session token
    token = secrets.token_urlsafe(32)
    sessions = _load_sessions()
    
    # Session expires in 30 days
    expiry = (datetime.now() + timedelta(days=30)).isoformat()
    
    sessions[token] = {
        "username": username,
        "user_id": username,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry
    }
    
    _save_sessions(sessions)
    
    return True, "Login successful", {
        "token": token,
        "username": username,
        "user_id": username,
        "email": user.get("email")
    }


def verify_session(token: str) -> tuple[bool, dict]:
    """
    Verify a session token and return user info.
    
    Returns:
        (valid: bool, user_data: dict)
    """
    if not token:
        return False, {}
    
    sessions = _load_sessions()
    
    if token not in sessions:
        return False, {}
    
    session = sessions[token]
    
    # Check if session has expired
    expiry = datetime.fromisoformat(session["expires_at"])
    if datetime.now() > expiry:
        # Remove expired session
        del sessions[token]
        _save_sessions(sessions)
        return False, {}
    
    return True, {
        "username": session["username"],
        "user_id": session["user_id"]
    }


def logout_user(token: str) -> bool:
    """Remove a session token (logout)."""
    sessions = _load_sessions()
    
    if token in sessions:
        del sessions[token]
        _save_sessions(sessions)
        return True
    
    return False


def get_user_info(username: str) -> dict:
    """Get user information (excluding password)."""
    users = _load_users()
    
    if username not in users:
        return {}
    
    user = users[username].copy()
    user.pop("password_hash", None)
    return user


def update_user_profile(username: str, profile_data: dict) -> tuple[bool, str]:
    """Update user's onboarding profile information.
    
    Args:
        username: User's username
        profile_data: Dict with keys like 'allergies', 'medications_to_avoid', 
                     'blood_group', 'conditions', 'ongoing_issues', 'doctor', 'loved_ones'
    
    Returns:
        (success: bool, message: str)
    """
    users = _load_users()
    
    if username not in users:
        return False, "User not found"
    
    if "profile" not in users[username]:
        users[username]["profile"] = {
            "onboarding_complete": False,
            "medical_data": {},
            "emergency_contacts": {},
            "preferences": {}
        }
    
    # Update medical data
    if "allergies" in profile_data:
        users[username]["profile"]["medical_data"]["allergies"] = profile_data["allergies"]
    
    if "medications_to_avoid" in profile_data:
        users[username]["profile"]["medical_data"]["medications_to_avoid"] = profile_data["medications_to_avoid"]
    
    if "blood_group" in profile_data:
        users[username]["profile"]["medical_data"]["blood_group"] = profile_data["blood_group"]
    
    if "conditions" in profile_data:
        users[username]["profile"]["medical_data"]["conditions"] = profile_data["conditions"]
    
    if "ongoing_issues" in profile_data:
        users[username]["profile"]["medical_data"]["ongoing_issues"] = profile_data["ongoing_issues"]
    
    # Update emergency contacts
    if "doctor" in profile_data:
        users[username]["profile"]["emergency_contacts"]["doctor"] = profile_data["doctor"]
    
    if "loved_ones" in profile_data:
        users[username]["profile"]["emergency_contacts"]["loved_ones"] = profile_data["loved_ones"]
    
    if "consent_given" in profile_data:
        users[username]["profile"]["emergency_contacts"]["consent_given"] = profile_data["consent_given"]
    
    # Update preferences
    if "language" in profile_data:
        users[username]["profile"]["preferences"]["language"] = profile_data["language"]
    
    if "output_mode" in profile_data:
        users[username]["profile"]["preferences"]["output_mode"] = profile_data["output_mode"]
    
    # Mark onboarding as complete if we have substantial data
    if profile_data.get("mark_complete", False):
        users[username]["profile"]["onboarding_complete"] = True
    
    users[username]["updated_at"] = datetime.now().isoformat()
    
    _save_users(users)
    return True, "Profile updated successfully"


def get_user_profile_context(username: str) -> str:
    """Get formatted user profile context for AI agent.
    
    Returns a formatted string with user's medical info for context.
    """
    users = _load_users()
    
    if username not in users or "profile" not in users[username]:
        return ""
    
    profile = users[username]["profile"]
    medical = profile.get("medical_data", {})
    
    context_parts = []
    
    if medical.get("allergies"):
        context_parts.append(f"Allergies: {', '.join(medical['allergies'])}")
    
    if medical.get("medications_to_avoid"):
        context_parts.append(f"Medications to avoid: {', '.join(medical['medications_to_avoid'])}")
    
    if medical.get("blood_group"):
        context_parts.append(f"Blood group: {medical['blood_group']}")
    
    if medical.get("conditions"):
        context_parts.append(f"Medical conditions: {', '.join(medical['conditions'])}")
    
    if medical.get("ongoing_issues"):
        context_parts.append(f"Ongoing issues: {', '.join(medical['ongoing_issues'])}")
    
    return "\n".join(context_parts) if context_parts else ""


def get_emergency_contacts(username: str) -> dict:
    """Get user's emergency contacts.
    
    Returns:
        dict with 'consent_given', 'doctor', and 'loved_ones'
    """
    users = _load_users()
    
    if username not in users or "profile" not in users[username]:
        return {"consent_given": False, "doctor": {}, "loved_ones": []}
    
    return users[username]["profile"].get("emergency_contacts", {
        "consent_given": False,
        "doctor": {},
        "loved_ones": []
    })


def has_emergency_consent(username: str) -> bool:
    """Check if user has given consent for emergency contact alerts."""
    contacts = get_emergency_contacts(username)
    return contacts.get("consent_given", False)
