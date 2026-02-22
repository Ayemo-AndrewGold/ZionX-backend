"""Thread/session management for tracking recent conversations."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

THREADS_DIR = "user_threads"


def _ensure_threads_dir():
    """Ensure the threads directory exists."""
    Path(THREADS_DIR).mkdir(exist_ok=True)


def _get_user_threads_file(user_id: str) -> Path:
    """Get the path to a user's threads file."""
    return Path(THREADS_DIR) / f"{user_id}_threads.json"


def save_thread_metadata(user_id: str, thread_id: str, title: str, last_message: Optional[str] = None) -> None:
    """Save or update thread metadata for a user.
    
    Args:
        user_id: User identifier
        thread_id: Thread/conversation identifier
        title: Title for the thread (usually first user message)
        last_message: Optional last message preview
    """
    try:
        _ensure_threads_dir()
        threads_file = _get_user_threads_file(user_id)
        
        # Load existing threads
        threads = {}
        if threads_file.exists():
            try:
                threads = json.loads(threads_file.read_text())
            except json.JSONDecodeError:
                threads = {}
        
        # Update or create thread metadata
        if thread_id in threads:
            # Update existing thread
            threads[thread_id]["last_updated"] = datetime.now().isoformat()
            if last_message:
                threads[thread_id]["last_message"] = last_message
        else:
            # Create new thread
            threads[thread_id] = {
                "thread_id": thread_id,
                "title": title[:100],  # Limit title length
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "last_message": last_message[:200] if last_message else "",
                "message_count": 1
            }
        
        # Save back to file
        threads_file.write_text(json.dumps(threads, indent=2))
    except Exception as e:
        print(f"Error saving thread metadata: {e}")


def get_recent_threads(user_id: str, limit: int = 10) -> List[Dict]:
    """Get recent threads for a user, sorted by last_updated.
    
    Args:
        user_id: User identifier
        limit: Maximum number of threads to return
        
    Returns:
        List of thread metadata dicts
    """
    try:
        threads_file = _get_user_threads_file(user_id)
        
        if not threads_file.exists():
            return []
        
        threads = json.loads(threads_file.read_text())
        
        # Convert to list and sort by last_updated
        threads_list = list(threads.values())
        threads_list.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        
        return threads_list[:limit]
    except Exception as e:
        print(f"Error getting recent threads: {e}")
        return []


def increment_thread_message_count(user_id: str, thread_id: str) -> None:
    """Increment the message count for a thread.
    
    Args:
        user_id: User identifier
        thread_id: Thread identifier
    """
    try:
        threads_file = _get_user_threads_file(user_id)
        
        if not threads_file.exists():
            return
        
        threads = json.loads(threads_file.read_text())
        
        if thread_id in threads:
            threads[thread_id]["message_count"] = threads[thread_id].get("message_count", 0) + 1
            threads[thread_id]["last_updated"] = datetime.now().isoformat()
            threads_file.write_text(json.dumps(threads, indent=2))
    except Exception as e:
        print(f"Error incrementing thread message count: {e}")


def get_thread_metadata(user_id: str, thread_id: str) -> Optional[Dict]:
    """Get metadata for a specific thread.
    
    Args:
        user_id: User identifier
        thread_id: Thread identifier
        
    Returns:
        Thread metadata dict or None if not found
    """
    try:
        threads_file = _get_user_threads_file(user_id)
        
        if not threads_file.exists():
            return None
        
        threads = json.loads(threads_file.read_text())
        return threads.get(thread_id)
    except Exception as e:
        print(f"Error getting thread metadata: {e}")
        return None
