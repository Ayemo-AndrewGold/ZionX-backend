from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from spitch import Spitch
from dotenv import load_dotenv
import os
import io
from functools import wraps

# Load environment variables from .env file
load_dotenv()

from core.config import MODEL_NAME
from main import run, get_chat_history
from memory import load_facts, get_all_users, delete_thread_memory, save_fact
from document_extractor import extract_document_content
from services.ai_service import extract_health_facts_with_ai, translate_to_english
from users import register_user, login_user, logout_user, verify_session, get_user_info, update_user_profile
from daily_tracking import save_daily_tracking, load_tracking_history, get_tracking_summary
from risk_monitor import load_risk_history, get_risk_summary
from alert_history import load_alert_history, get_alerts_summary
from thread_manager import save_thread_metadata, get_recent_threads, increment_thread_message_count

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

spitch_client = Spitch() if os.getenv("SPITCH_API_KEY") else None

# Supported Nigerian languages
SUPPORTED_LANGUAGES = {
    'yo': {'name': 'Yoruba', 'voice': 'sade'},
    'ha': {'name': 'Hausa', 'voice': 'amina'},
    'ig': {'name': 'Igbo', 'voice': 'ada'},
    'en': {'name': 'English', 'voice': 'lily'}
}


def get_authenticated_user():
    """Parse the Bearer token from the request and return the user dict, or None."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.replace('Bearer ', '')
    valid, user_data = verify_session(token)
    return user_data if valid else None


def require_auth(f):
    """Decorator that enforces authentication and injects the user dict as the first argument."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return {"error": "Not authenticated"}, 401
        return f(user, *args, **kwargs)
    return wrapper


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


# ── Authentication Endpoints ──

@app.post("/auth/register")
def register():
    """Register a new user."""
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()
    email = body.get("email", "").strip() or None
    
    success, message = register_user(username, password, email)
    
    if success:
        return {"ok": True, "message": message}, 201
    else:
        return {"error": message}, 400


@app.post("/auth/login")
def login():
    """Authenticate a user and return a session token."""
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()
    
    success, message, user_data = login_user(username, password)
    
    if success:
        return {"ok": True, "message": message, "user": user_data}
    else:
        return {"error": message}, 401


@app.post("/auth/logout")
def logout():
    """Logout a user by invalidating their session token."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"error": "No authorization token provided"}, 401
    
    token = auth_header.replace('Bearer ', '')
    success = logout_user(token)
    
    if success:
        return {"ok": True, "message": "Logged out successfully"}
    else:
        return {"error": "Invalid session"}, 400


@app.get("/auth/verify")
@require_auth
def verify(user):
    """Verify if a session token is valid."""
    return {"ok": True, "user": user}


@app.get("/auth/me")
@require_auth
def get_me(user):
    """Get current authenticated user info."""
    user_info = get_user_info(user["username"])
    return {"user": user_info}


# ── Onboarding & Profile Endpoints ──

@app.post("/onboarding/profile")
@require_auth
def update_onboarding_profile(user):
    """Update user's onboarding profile with medical data and preferences."""
    body = request.get_json(silent=True) or {}
    
    # Extract profile data
    profile_data = {
        "allergies": body.get("allergies", []),
        "medications_to_avoid": body.get("medications_to_avoid", []),
        "blood_group": body.get("blood_group"),
        "conditions": body.get("conditions", []),
        "ongoing_issues": body.get("ongoing_issues", []),
        "language": body.get("language", "en"),
        "output_mode": body.get("output_mode", "text"),
        "mark_complete": body.get("mark_complete", False)
    }
    
    # Handle emergency contacts separately
    if "emergency_contacts" in body:
        ec = body["emergency_contacts"]
        profile_data["consent_given"] = ec.get("consent_given", False)
        profile_data["doctor"] = ec.get("doctor", {})
        profile_data["loved_ones"] = ec.get("loved_ones", [])
    
    success, message = update_user_profile(user["username"], profile_data)
    
    if success:
        return {"ok": True, "message": message}
    else:
        return {"error": message}, 400


@app.get("/onboarding/profile")
@require_auth
def get_onboarding_profile(user):
    """Get user's onboarding profile."""
    user_info = get_user_info(user["username"])
    profile = user_info.get("profile", {})
    return {"ok": True, "profile": profile}


# ── Daily Tracking Endpoints ──

@app.post("/tracking/daily")
@require_auth
def submit_daily_tracking(user):
    """Submit daily health tracking data."""
    body = request.get_json(silent=True) or {}

    tracking_data = {
        "mood": body.get("mood"),
        "symptoms": body.get("symptoms", []),
        "energy": body.get("energy"),
        "medications": body.get("medications", []),
        "notes": body.get("notes", "")
    }

    entry = save_daily_tracking(user["user_id"], tracking_data)

    if entry:
        return {"ok": True, "entry": entry, "message": "Tracking data saved"}
    return {"error": "Failed to save tracking data"}, 500


@app.get("/tracking/history")
@require_auth
def get_tracking_history(user):
    """Get user's tracking history."""
    days = request.args.get("days", type=int)
    entries = load_tracking_history(user["user_id"], days=days)
    return {"ok": True, "entries": entries, "count": len(entries)}


@app.get("/tracking/summary")
@require_auth
def get_tracking_summary_endpoint(user):
    """Get formatted summary of recent tracking data."""
    days = request.args.get("days", 7, type=int)
    summary = get_tracking_summary(user["user_id"], days=days)
    return {"ok": True, "summary": summary}


# ── Risk Monitor Endpoints ──

@app.get("/risk/history")
@require_auth
def get_risk_history(user):
    """Get user's risk assessment history."""
    days = request.args.get("days", type=int)
    assessments = load_risk_history(user["user_id"], days=days)
    return {"ok": True, "assessments": assessments, "count": len(assessments)}


@app.get("/risk/summary")
@require_auth
def get_risk_summary_endpoint(user):
    """Get summary statistics of risk assessments."""
    days = request.args.get("days", 30, type=int)
    summary = get_risk_summary(user["user_id"], days=days)
    return {"ok": True, "summary": summary}


# ── Emergency Alerts Endpoints ──

@app.get("/alerts/history")
@require_auth
def get_alerts_history(user):
    """Get user's emergency alert history."""
    days = request.args.get("days", type=int)
    alerts = load_alert_history(user["user_id"], days=days)
    return {"ok": True, "alerts": alerts, "count": len(alerts)}


@app.get("/alerts/summary")
@require_auth
def get_alerts_summary_endpoint(user):
    """Get summary statistics of emergency alerts."""
    days = request.args.get("days", 30, type=int)
    summary = get_alerts_summary(user["user_id"], days=days)
    return {"ok": True, "summary": summary}


@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    if not message:
        return {"error": "message is required"}, 400

    thread_id = body.get("thread_id", "default")
    
    # Get authenticated user or use provided user_id or default to guest
    user = get_authenticated_user()
    if user:
        user_id = user["user_id"]
    else:
        user_id = body.get("user_id", "guest")
    
    try:
        # Check if this is a new thread (no existing metadata)
        from thread_manager import get_thread_metadata
        existing_thread = get_thread_metadata(user_id, thread_id)
        
        # Save thread metadata (creates new or updates existing)
        if not existing_thread:
            # New thread - use first message as title
            save_thread_metadata(user_id, thread_id, message, message)
        else:
            # Existing thread - just increment count and update timestamp
            increment_thread_message_count(user_id, thread_id)
        
        response = run(message, thread_id=thread_id, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}, 500

    return response


@app.get("/chat/history")
def get_history():
    """Get chat history for a specific thread."""
    thread_id = request.args.get("thread_id", "default")
    
    try:
        history = get_chat_history(thread_id)
        return {"ok": True, "messages": history, "thread_id": thread_id}
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.get("/chat/recent")
@require_auth
def get_recent_chats(user):
    """Get recent chat threads/conversations for the authenticated user."""
    limit = request.args.get("limit", 10, type=int)
    
    try:
        threads = get_recent_threads(user["user_id"], limit=limit)
        return {"ok": True, "threads": threads, "count": len(threads)}
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.get("/memory")
def get_memory():
    """Get long-term memory/facts for a specific user."""
    # Get authenticated user or use provided user_id or default to guest
    user = get_authenticated_user()
    if user:
        user_id = user["user_id"]
    else:
        user_id = request.args.get("user_id", "guest")
    
    facts = load_facts(user_id)
    return {"user_id": user_id, "facts": facts or ""}


@app.post("/upload")
def upload_document():
    """Upload a document and append its content to user's long-term memory."""
    # Get authenticated user or use provided user_id or default to guest
    user = get_authenticated_user()
    if user:
        user_id = user["user_id"]
    else:
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


@app.post("/speech/transcribe")
def transcribe_audio():
    """Convert speech to text using Spitch API, then translate to English."""
    if not spitch_client:
        return {"error": "Speech service not configured"}, 503
    
    if 'audio' not in request.files:
        return {"error": "No audio file provided"}, 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'yo')  # Default to Yoruba
    
    if language not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"}, 400
    
    try:
        audio_content = audio_file.read()
        
        # Step 1: Transcribe audio in the original language
        response = spitch_client.speech.transcribe(
            language=language,
            content=audio_content,
            timestamp="sentence"
        )
        
        original_text = response.text
        
        # Step 2: Translate to English if not already in English
        english_text = translate_to_english(original_text, language)
        
        return {
            "ok": True,
            "text": english_text,
            "original_text": original_text if language != 'en' else None,
            "language": language
        }
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.post("/speech/generate")
def generate_speech():
    """
    Convert English text to speech in target language using Spitch API.
    Process: English text → translate to target language → generate speech
    """
    if not spitch_client:
        return {"error": "Speech service not configured"}, 503
    
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    language = body.get("language", "yo")
    audio_format = body.get("format", "mp3")
    
    if not text:
        return {"error": "text is required"}, 400
    
    if language not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"}, 400
    
    try:
        # Step 1: Translate English text to target language (if not already English)
        if language != 'en':
            translation = spitch_client.text.translate(
                text=text,
                source="en",
                target=language
            )
            translated_text = translation.text
        else:
            translated_text = text
        
        # Step 2: Generate speech from the translated text
        voice = SUPPORTED_LANGUAGES[language]['voice']
        response = spitch_client.speech.generate(
            text=translated_text,
            language=language,
            voice=voice,
            format=audio_format
        )
        
        audio_data = response.read()
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype=f'audio/{audio_format}',
            as_attachment=False,
            download_name=f'speech.{audio_format}'
        )
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.get("/speech/languages")
def get_supported_languages():
    """Get list of supported languages for voice interaction."""
    return {
        "languages": [
            {"code": code, "name": info["name"], "voice": info["voice"]}
            for code, info in SUPPORTED_LANGUAGES.items()
        ]
    }



@app.errorhandler(404)
def not_found(exc):
    return {"error": "not found"}, 404


@app.errorhandler(405)
def method_not_allowed(exc):
    return {"error": "method not allowed"}, 405


if __name__ == "__main__":
    app.run(debug=True)
