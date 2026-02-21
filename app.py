

from flask import Flask, request
from flask_cors import CORS

from agent_config import AgentConfig
from main import run

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
    try:
        response = run(message, thread_id=thread_id)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}, 500

    return {"response": response}



@app.errorhandler(404)
def not_found(exc):
    return {"error": "not found"}, 404


@app.errorhandler(405)
def method_not_allowed(exc):
    return {"error": "method not allowed"}, 405


if __name__ == "__main__":
    app.run(debug=True)
