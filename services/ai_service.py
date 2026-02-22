"""AI-powered document analysis and translation services.

These functions use the shared specialist LLM factory so they benefit from
the same caching and configuration as the specialist tools.
"""
from tools.specialist_utils import get_specialist


def extract_health_facts_with_ai(content: str, filename: str) -> str:
    """Extract important long-term health facts from a document using AI."""
    try:
        llm = get_specialist("doc_extractor")
        prompt = (
            f"Analyze the following document and extract ONLY important long-term facts "
            f"that should be remembered about the user's health.\n\n"
            f"Document: {filename}\n\n"
            f"Content:\n{content[:4000]}\n\n"
            f"If no significant health information is found, return the text 'None'."
        )
        response = llm.invoke(prompt).content
        return f"\n--- {filename} ---\n{response}\n\n"
    except Exception as e:
        print(f"Error extracting facts with AI: {e}")
        return ""


def translate_to_english(text: str, source_language: str) -> str:
    """Translate text from a supported Nigerian language to English using AI.

    Returns the original text unchanged if the source language is English
    or if translation fails.
    """
    if source_language == "en":
        return text

    language_names = {"yo": "Yoruba", "ha": "Hausa", "ig": "Igbo"}
    lang_name = language_names.get(source_language, source_language)

    try:
        llm = get_specialist("translator", temperature=0.1)
        prompt = (
            f"Translate the following {lang_name} text to English.\n"
            f"Provide ONLY the English translation, nothing else.\n\n"
            f"{lang_name} text: {text}\n\n"
            f"English translation:"
        )
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text
