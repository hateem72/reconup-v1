import sys
import logging

class StructuredConsoleFormatter(logging.Formatter):
    """Formats console logs with timestamp and stage tags."""
    def format(self, record):
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        stage = getattr(record, "stage", "SYSTEM")
        return f"[{timestamp}] [{stage}] {record.getMessage()}"

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
    extra = {"stage": stage.upper()}
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
