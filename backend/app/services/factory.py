import os
from app.core.config import settings

def get_model_manager_class():
    """
    Get the appropriate ModelManager class based on configuration.
    
    Logic:
    1. If USE_LIGHTWEIGHT_MANAGER env var is set, respect it (override).
    2. Else, check settings.USE_GPU (auto-detected).
       - If GPU available -> ModelManager (vLLM)
       - If GPU missing -> LightweightModelManager (CPU/Transformers)
    """
    env_force_lightweight = os.getenv("USE_LIGHTWEIGHT_MANAGER")
    
    if env_force_lightweight is not None:
        use_lightweight = env_force_lightweight.lower() == "true"
        # print(f"🔧 Manager selection overridden by env var: {'Lightweight' if use_lightweight else 'Full'}")
    else:
        use_lightweight = not settings.USE_GPU
        # print(f"🔧 Auto-detected manager: {'Lightweight (CPU)' if use_lightweight else 'Full (GPU)'}")
        
    if use_lightweight:
        from app.services.lightweight_model_manager import LightweightModelManager
        return LightweightModelManager
    else:
        from app.services.model_manager import ModelManager
        return ModelManager

def get_model_manager():
    """
    Get the singleton instance of the appropriate ModelManager.
    """
    ManagerClass = get_model_manager_class()
    return ManagerClass()
