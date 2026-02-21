"""Simple file-based long-term memory per thread."""

import os
from pathlib import Path

MEMORY_DIR = "memory"


def load_facts(thread_id: str) -> str | None:
    """Load all stored facts for a thread."""
    try:
        path = Path(MEMORY_DIR) / f"{thread_id}.txt"
        if not path.exists():
            return None
        content = path.read_text().strip()
        return content or None
    except Exception as e:
        print(f"Error loading facts for {thread_id}: {e}")
        return None


def save_fact(thread_id: str, fact: str) -> None:
    """Append a new fact to the thread's memory file."""
    try:
        Path(MEMORY_DIR).mkdir(exist_ok=True)
        path = Path(MEMORY_DIR) / f"{thread_id}.txt"
        with path.open("a") as f:
            f.write(fact.strip() + "\n")
    except Exception as e:
        print(f"Error saving fact for {thread_id}: {e}")
