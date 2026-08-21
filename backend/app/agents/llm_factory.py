import os
from typing import Optional
from langchain_community.llms import Ollama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage

class MockFinanceLLM:
    """Fallback Mock LLM when Ollama is unavailable during unit testing."""
    def invoke(self, input_data: str) -> AIMessage:
        return AIMessage(content="Financial analysis completed based on deterministic facts. No hallucinated records.")

    def bind_tools(self, tools: list):
        return self

def get_llm(model_name: Optional[str] = None, temperature: float = 0.0):
    """
    Returns configured Ollama LLM or Mock fallback for offline testing.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    target_model = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    try:
        llm = Ollama(
            base_url=base_url,
            model=target_model,
            temperature=temperature
        )
        return llm
    except Exception:
        return MockFinanceLLM()
