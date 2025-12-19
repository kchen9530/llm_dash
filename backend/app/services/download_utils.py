"""
Download utility for tracking model download progress
"""
import tqdm
import os
from app.services.model_logger import model_logger

class DownloadProgress:
    """
    Custom TQDM-like class to capture download progress and send to logger
    """
    def __init__(self, model_id: str, desc: str = "Downloading", total: int = 0, unit: str = "B", unit_scale: bool = False, unit_divisor: int = 1000, **kwargs):
        self.model_id = model_id
        self.desc = desc
        self.total = total
        self.current = 0
        self.unit = unit
        self.last_percent = -1
        
        # Initial log
        model_logger.add_log(model_id, f"📥 Started {desc}...", "INFO")
        
    def update(self, n: int = 1):
        """Update progress"""
        self.current += n
        if self.total > 0:
            percent = int((self.current / self.total) * 100)
            # Log every 5% to avoid spamming
            if percent > self.last_percent and percent % 5 == 0:
                self.last_percent = percent
                model_logger.add_log(self.model_id, f"📥 {self.desc}: {percent}% completed", "INFO")
    
    def close(self):
        """Finish download"""
        model_logger.add_log(self.model_id, f"✅ {self.desc} completed!", "INFO")

    @classmethod
    def get_tqdm_class(cls, model_id: str):
        """Factory to create a TQDM class bound to a specific model_id"""
        class BoundTqdm(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(model_id, *args, **kwargs)
        return BoundTqdm
