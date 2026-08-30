from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ReconUp Engine",
        "version": "1.0.0"
    }

@router.get("/metrics")
def get_system_metrics():
    return {
        "system_status": "ONLINE",
        "engine": "Deterministic Finance Engine v1.0",
        "agent_orchestration": "LangGraph v0.1",
        "llm": "Local Ollama qwen2.5:7b"
    }
