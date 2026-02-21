"""Simple file-based long-term memory per thread."""

import os

MEMORY_DIR = "memory"


def load_facts(thread_id: str) -> str | None:
    path = os.path.join(MEMORY_DIR, f"{thread_id}.txt")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        content = f.read().strip()
    return content or None


def save_fact(thread_id: str, fact: str) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = os.path.join(MEMORY_DIR, f"{thread_id}.txt")
    with open(path, "a") as f:
        f.write(fact.strip() + "\n")
