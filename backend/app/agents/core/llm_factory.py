import os
import logging
from dataclasses import dataclass
from typing import Any
import httpx
from app.core.config import settings
from app.core.logging import log_stage

logger = logging.getLogger(__name__)


@dataclass
class GeminiResponse:
    content: str


class GeminiRESTLLM:
    """
    Lightweight, high-speed REST client wrapper for Google Gemini API (v1beta).
    Directly calls Google Generative AI REST endpoints with zero third-party dependencies.
    Returns an object with .content attribute to match LangChain duck typing.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash", temperature: float = 0.0):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

    def invoke(self, prompt: Any) -> GeminiResponse:
        prompt_text = getattr(prompt, "content", str(prompt))
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt_text}]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature
            }
        }
        headers = {"Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    json=payload,
                    headers=headers
                )
                res.raise_for_status()
                data = res.json()
                text_out = ""
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_out = parts[0].get("text", "")
                return GeminiResponse(content=text_out)
        except Exception as e:
            log_stage("AGENT", f"Gemini API invocation error: {str(e)}", level="error")
            raise e


def get_llm(temperature: float = 0.0):
    """
    Returns configured LLM instance based on settings.LLM_PROVIDER.
    Supports 'gemini' and 'ollama' (default).
    """
    provider = getattr(settings, "LLM_PROVIDER", "ollama").lower().strip()

    if provider == "gemini":
        api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash") or "gemini-3.5-flash"

        if not api_key:
            log_stage("AGENT", "GEMINI_API_KEY is not configured in .env. Falling back to local Ollama LLM.", level="warn")
        else:
            # Try loading langchain-google-genai dynamically if available
            try:
                import importlib
                mod = importlib.import_module("langchain_google_genai")
                ChatGoogleGenerativeAI = getattr(mod, "ChatGoogleGenerativeAI")
                log_stage("AGENT", f"Initializing Gemini LLM ({model_name}) via langchain-google-genai")
                return ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=temperature
                )
            except Exception:
                log_stage("AGENT", f"Initializing Gemini LLM ({model_name}) via Native REST Client")
                return GeminiRESTLLM(
                    api_key=api_key,
                    model_name=model_name,
                    temperature=temperature
                )

    # Default: Ollama Local LLM
    from langchain_community.llms import Ollama
    model_name = getattr(settings, "LLM_MODEL", "qwen2.5:3b") or "qwen2.5:3b"
    base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434") or "http://localhost:11434"

    return Ollama(
        model=model_name,
        base_url=base_url,
        temperature=temperature
    )
