"""
Model Logger - Captures logs for each model instance
"""
import logging
from typing import Dict, List
from collections import deque
from datetime import datetime


class ModelLogger:
    """
    Centralized logger for model instances.
    Captures logs in memory for each model.
    """
    
    _instance = None
    _logs: Dict[str, deque] = {}
    _max_logs_per_model = 500  # Keep last 500 logs per model
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._logs = {}
    
    def add_log(self, model_id: str, message: str, level: str = "INFO"):
        """Add a log entry for a specific model"""
        if model_id not in self._logs:
            self._logs[model_id] = deque(maxlen=self._max_logs_per_model)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self._logs[model_id].append(log_entry)
    
    def get_logs(self, model_id: str, lines: int = 500) -> List[str]:
        """Get logs for a specific model (last N lines)"""
        if model_id not in self._logs:
            return []
        all_logs = list(self._logs[model_id])
        return all_logs[-lines:] if lines > 0 else all_logs
    
    def clear_logs(self, model_id: str):
        """Clear logs for a specific model"""
        if model_id in self._logs:
            self._logs[model_id].clear()
    
    def remove_model(self, model_id: str):
        """Remove all logs for a model (when model is deleted)"""
        if model_id in self._logs:
            del self._logs[model_id]


# Global instance
model_logger = ModelLogger()

