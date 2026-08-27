import sys
import logging
from typing import Optional

_current_batch_context = {"batch_id": None, "db_session": None}

def set_audit_context(batch_id: Optional[str], db_session=None):
    """Sets current batch_id and DB session for automatic log audit persistence."""
    _current_batch_context["batch_id"] = batch_id
    _current_batch_context["db_session"] = db_session

def clear_audit_context():
    """Clears current batch context."""
    _current_batch_context["batch_id"] = None
    _current_batch_context["db_session"] = None

class StructuredConsoleFormatter(logging.Formatter):
    """Formats console logs with timestamp and stage tags."""
    def format(self, record):
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        stage = getattr(record, "stage", "SYSTEM")
        msg = record.getMessage()
        msg_clean = msg.replace("₹", "INR ")
        return f"[{timestamp}] [{stage}] {msg_clean}"

def setup_logger(name: str = "finance_controller", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredConsoleFormatter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()

def log_stage(stage: str, message: str, level: str = "info"):
    """Logs structured stage message to console AND persists to database audit events."""
    extra = {"stage": stage.upper()}
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)

    # Automatically persist to DB AuditEventModel if batch context is active
    batch_id = _current_batch_context.get("batch_id")
    db_session = _current_batch_context.get("db_session")
    if batch_id and db_session:
        try:
            from app.database.repositories import FinanceRepository
            repo = FinanceRepository(db_session)
            repo.log_audit_event(batch_id, "LOG", stage.upper(), message)
        except Exception:
            pass

def log_agent_call(agent_name: str, task: str, input_summary: str, output_summary: str, confidence: float, duration_sec: float):
    """Logs structured AI call execution metrics per requirements."""
    log_stage("AGENT", f"Agent: {agent_name} | Task: {task}")
    log_stage("AGENT", f"  Input: {input_summary}")
    log_stage("AGENT", f"  Output: {output_summary}")
    log_stage("AGENT", f"  Confidence: {round(confidence, 2)} | Duration: {round(duration_sec, 3)}s | Status: SUCCESS")
