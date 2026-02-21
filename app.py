"""Flask entry point for the ZionX healthcare assistant API.

Run:
    flask --app app run --debug
    # or in production:
    gunicorn app:app
"""

import json
from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS

from agent_config import AgentConfig
from main import get_agent, run

app = Flask(__name__)
CORS(app)

_config = AgentConfig.from_env()


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": _config.model_name}


# ── Chat (blocking) ───────────────────────────────────────────────────────────

@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    if not message:
        return {"error": "message is required"}, 400

    thread_id = body.get("thread_id", "default")
    try:
        response = run(message, thread_id=thread_id)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}, 500

    return {"response": response}


# ── Chat (streaming / SSE) ────────────────────────────────────────────────────

@app.post("/chat/stream")
def chat_stream():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    if not message:
        return {"error": "message is required"}, 400

    thread_id = body.get("thread_id", "default")
    config = {"configurable": {"thread_id": thread_id}}

    def generate():
        try:
            agent = get_agent()
            for chunk, _ in agent.stream(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
                stream_mode="messages",
            ):
                # Only forward AI message tokens (not tool calls, etc.)
                token = getattr(chunk, "content", None)
                if token:
                    yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(exc):
    return {"error": "not found"}, 404


@app.errorhandler(405)
def method_not_allowed(exc):
    return {"error": "method not allowed"}, 405


# ── Dev server ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
