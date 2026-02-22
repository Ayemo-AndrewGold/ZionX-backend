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
        "user_id": username  # Use username as user_id for simplicity
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
