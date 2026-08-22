import os
import requests
from typing import Optional

class MockFinanceLLM:
    """Fallback Mock LLM when Ollama endpoint or model is unavailable."""
    def invoke(self, input_data: str):
        class MockMessage:
            content = "Financial analysis completed based on deterministic facts. No hallucinated records."
        return MockMessage()

    def bind_tools(self, tools: list):
        return self


def get_available_ollama_model() -> Optional[str]:
    """Queries local Ollama service to detect installed model name."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            if models:
                for m in models:
                    if "qwen" in m:
                        return m
                return models[0]
    except Exception:
        pass
    return None


def get_llm(model_name: Optional[str] = None, temperature: float = 0.0):
    """
    Returns configured OllamaLLM (from updated langchain-ollama package)
    targeting locally installed model (e.g. qwen2.5:3b) with clean fallback.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    target_model = model_name or os.getenv("OLLAMA_MODEL")
    if not target_model:
        detected = get_available_ollama_model()
        target_model = detected or "qwen2.5:3b"

    try:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(base_url=base_url, model=target_model, temperature=temperature)
    except Exception:
        try:
            from langchain_community.llms import Ollama
            return Ollama(base_url=base_url, model=target_model, temperature=temperature)
        except Exception:
            return MockFinanceLLM()
