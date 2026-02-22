"""Simple file-based long-term memory per thread."""

from pathlib import Path

MEMORY_DIR = "memory"


def load_facts(user_id: str) -> str | None:
    """Load all stored facts for a user."""
    try:
        path = Path(MEMORY_DIR) / f"{user_id}.txt"
        if not path.exists():
            return None
        content = path.read_text().strip()
        return content or None
    except Exception as e:
        print(f"Error loading facts for {user_id}: {e}")
        return None


def save_fact(user_id: str, fact: str) -> None:
    """Append a new fact to the user's memory file."""
    try:
        Path(MEMORY_DIR).mkdir(exist_ok=True)
        path = Path(MEMORY_DIR) / f"{user_id}.txt"
        with path.open("a") as f:
            f.write(fact.strip() + "\n")
    except Exception as e:
        print(f"Error saving fact for {user_id}: {e}")


def get_all_users() -> list[dict]:
    """Get a list of all users with their memory metadata."""
    try:
        memory_path = Path(MEMORY_DIR)
        if not memory_path.exists():
            return []
        
        users = []
        for file in memory_path.glob("*.txt"):
            user_id = file.stem
            mtime = file.stat().st_mtime
            try:
                with file.open() as f:
                    first_line = f.readline().strip()
                    preview = first_line[:100] if first_line else "No content"
            except Exception:
                preview = "Error reading file"
            
            users.append({
                "user_id": user_id,
                "last_updated": mtime,
                "preview": preview
            })
        
        users.sort(key=lambda x: x["last_updated"], reverse=True)
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []


def delete_thread_memory(user_id: str) -> None:
    """Delete all memory for a specific user."""
    try:
        path = Path(MEMORY_DIR) / f"{user_id}.txt"
        if path.exists():
            path.unlink()
    except Exception as e:
        print(f"Error deleting memory for {user_id}: {e}")
        raise
