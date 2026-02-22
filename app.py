from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from langchain_google_genai import ChatGoogleGenerativeAI

from agent_config import AgentConfig
from main import run
from memory import load_facts, get_all_users, delete_thread_memory, save_fact
from document_extractor import extract_document_content

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

_config = AgentConfig.from_env()


def extract_health_facts_with_ai(content: str, filename: str) -> str:
    """Use AI to extract relevant health facts from document content."""
    try:
        llm = ChatGoogleGenerativeAI(
            model=_config.model_name,
            temperature=_config.temperature
        )
        
        prompt = f"""Analyze the following document and extract ONLY important long-term facts that should be remembered.
Extract and list ONLY
Document: {filename}

Content:
{content[:4000]}  # Limit to avoid token overflow

If no significan information is found return text 'None'
"""
        
        response = llm.invoke(prompt).text
        return f"\n--- {filename} ---\n{response}\n\n"
    except Exception as e:
        print(f"Error extracting facts with AI: {e}")
        return ""


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


@app.post("/upload")
def upload_document():
    """Upload a document and append its content to user's long-term memory."""
    user_id = request.form.get("user_id", "guest")
    extract_facts = request.form.get("extract_facts", "true").lower() == "true"
    
    if 'file' not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files['file']
    
    if file.filename == '':
        return {"error": "No selected file"}, 400
    
    if not allowed_file(file.filename):
        return {"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}, 400
    
    try:
        filename = secure_filename(file.filename)        
        content = extract_document_content(file, filename)
        
        extracted_facts = ""
        if extract_facts and content and not content.startswith("["):
            extracted_facts = extract_health_facts_with_ai(content, filename)
            if extracted_facts and "No significant health facts" not in extracted_facts:
                save_fact(user_id, extracted_facts)
        
        return {
            "ok": True, 
            "message": f"Document '{filename}' uploaded and processed",
            "user_id": user_id,
            "content_extracted": not content.startswith("["),
            "facts_extracted": bool(extracted_facts and "No significant health facts" not in extracted_facts)
        }
    
    except Exception as exc:
        return {"error": str(exc)}, 500


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
