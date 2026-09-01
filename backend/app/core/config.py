import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env from backend directory or project root
backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)
else:
    load_dotenv()

class Settings:
    # ─────────────────────────────────────────────────────────────────────────
    # REDIS CONFIGURATION
    # ─────────────────────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() in ("true", "1", "yes")
    REDIS_TTL_SECONDS: int = int(os.getenv("REDIS_TTL_SECONDS", "86400"))  # Default: 24 hours

    # ─────────────────────────────────────────────────────────────────────────
    # LLM PROVIDER & CREDENTIALS
    # ─────────────────────────────────────────────────────────────────────────
    # Options: "ollama", "openai", "gemini", "anthropic"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama").lower()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")

    # API Keys & Models
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")

    # Ollama Local Service URL
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance_controller.db")

settings = Settings()
