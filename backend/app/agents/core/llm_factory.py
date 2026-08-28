import os
from langchain_community.llms import Ollama
from app.core.config import settings

def get_llm(temperature: float = 0.0):
    """
    Returns configured local Ollama LLM instance (qwen2.5:3b).
    """
    model_name = getattr(settings, "LLM_MODEL", "qwen2.5:3b") or "qwen2.5:3b"
    base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434") or "http://localhost:11434"

    return Ollama(
        model=model_name,
        base_url=base_url,
        temperature=temperature
    )
