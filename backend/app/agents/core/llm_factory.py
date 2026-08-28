import logging
from app.core.config import settings

logger = logging.getLogger("finance_controller")

def get_llm(temperature: float = 0.0):
    """
    Pluggable LLM Factory: Returns configured LLM based on LLM_PROVIDER in .env.
    Supported providers:
      - 'ollama' (Local qwen2.5:3b)
      - 'openai' (gpt-4o-mini / gpt-4o)
      - 'gemini' (gemini-1.5-flash / gemini-1.5-pro)
      - 'anthropic' (claude-3-5-sonnet)
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL or "gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"OpenAI LLM initialization failed ({e}). Falling back to local Ollama.")

    elif provider in ("gemini", "google"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL or "gemini-1.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"Google Gemini LLM initialization failed ({e}). Falling back to local Ollama.")

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.LLM_MODEL or "claude-3-5-sonnet-20241022",
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"Anthropic LLM initialization failed ({e}). Falling back to local Ollama.")

    # Default / Local Ollama (qwen2.5:3b)
    from langchain_community.llms import Ollama
    return Ollama(
        model=settings.LLM_MODEL or "qwen2.5:3b",
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature
    )
