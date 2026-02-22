from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from langchain_google_genai import ChatGoogleGenerativeAI
from spitch import Spitch
from dotenv import load_dotenv
import os
import io

# Load environment variables from .env file
load_dotenv()

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

spitch_client = Spitch() if os.getenv("SPITCH_API_KEY") else None

# Supported Nigerian languages
SUPPORTED_LANGUAGES = {
    'yo': {'name': 'Yoruba', 'voice': 'sade'},
    'ha': {'name': 'Hausa', 'voice': 'amina'},
    'ig': {'name': 'Igbo', 'voice': 'ada'},
    'en': {'name': 'English', 'voice': 'lily'}
}


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


def translate_to_english(text: str, source_language: str) -> str:
    """Translate text from source language to English using Gemini AI."""
    if source_language == 'en':
        return text  # Already in English
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=_config.model_name,
            temperature=0.1
        )
        
        language_names = {
            'yo': 'Yoruba',
            'ha': 'Hausa',
            'ig': 'Igbo'
        }
        
        lang_name = language_names.get(source_language, source_language)
        
        prompt = f"""Translate the following {lang_name} text to English. 
Provide ONLY the English translation, nothing else.

{lang_name} text: {text}

English translation:"""
        
        response = llm.invoke(prompt).text.strip()
        return response
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


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
