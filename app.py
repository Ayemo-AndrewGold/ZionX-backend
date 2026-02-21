

from flask import Flask, request
from flask_cors import CORS

from agent_config import AgentConfig
from main import run
from memory import load_facts, get_all_users, delete_thread_memory

app = Flask(__name__)
CORS(app)

_config = AgentConfig.from_env()


@app.get("/health")
def health():
    return {"status": "ok", "model": _config.model_name}


@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    if not message:
        return {"error": "message is required"}, 400

    thread_id = body.get("thread_id", "default")
    user_id = body.get("user_id", "guest")
    try:
        response = run(message, thread_id=thread_id, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}, 500

    return {"response": response}


@app.get("/memory")
def get_memory():
    """Get long-term memory/facts for a specific user."""
    user_id = request.args.get("user_id", "guest")
    facts = load_facts(user_id)
    return {"user_id": user_id, "facts": facts or ""}


@app.get("/threads")
def list_threads():
    """List all available chat threads/sessions for a specific user."""
    user_id = request.args.get("user_id", "guest")
    # For now, return user's own thread (could be extended to support multiple threads per user)
    return {"threads": [{"thread_id": "main", "user_id": user_id}]}


@app.get("/users")
def list_users():
    """List all users with memory data."""
    users = get_all_users()
    return {"users": users}


@app.delete("/memory")
def delete_memory():
    """Delete all long-term memory for a specific user."""
    user_id = request.args.get("user_id")
    if not user_id:
        return {"error": "user_id is required"}, 400
    
    try:
        delete_thread_memory(user_id)
        return {"ok": True, "message": f"Memory deleted for user {user_id}"}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}, 500



@app.errorhandler(404)
def not_found(exc):
    return {"error": "not found"}, 404


@app.errorhandler(405)
def method_not_allowed(exc):
    return {"error": "method not allowed"}, 405


if __name__ == "__main__":
    app.run(debug=True)
