"""Shared utility for creating specialized LLM instances"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("SPECIALIST_MODEL", "gemini-3-flash-preview")
DEFAULT_TEMPERATURE = float(os.getenv("SPECIALIST_TEMPERATURE", "0.1"))


def get_specialist(
    specialist_type: str = None,
    model: str = None,
    temperature: float = None
) -> ChatGoogleGenerativeAI:
    """
    Get or create a specialist LLM instance with caching.
    
    Args:
        specialist_type: Optional type identifier for caching (e.g., 'pregnancy', 'diabetes')
        model: LLM model to use. Defaults to SPECIALIST_MODEL env var or 'gemini-2.0-flash-exp'
        temperature: Temperature setting. Defaults to SPECIALIST_TEMPERATURE env var or 0.3
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    model = model or DEFAULT_MODEL
    temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
    
    cache_key = f"_{specialist_type or 'default'}_specialist"
    
    if cache_key not in globals() or globals()[cache_key] is None:
        globals()[cache_key] = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
        )
    
    return globals()[cache_key]
