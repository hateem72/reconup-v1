import os
from langchain_community.llms import Ollama

def get_llm():
    """
    Returns a configured local Ollama LLM instance (qwen2.5:3b).
    Falls back gracefully if Ollama service is offline.
    """
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    return Ollama(
        model=model_name,
        base_url=base_url,
        temperature=0.0
    )
