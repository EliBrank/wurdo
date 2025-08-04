"""
Shared word engine singleton to eliminate duplicate loading
"""

import logging
from efficient_word_engine import EfficientWordEngine

logger = logging.getLogger(__name__)

# Global singleton instance
_global_word_engine = None

def get_shared_word_engine() -> EfficientWordEngine:
    """Get or create a global word engine instance."""
    global _global_word_engine
    
    if _global_word_engine is None:
        logger.info("Initializing shared word engine...")
        _global_word_engine = EfficientWordEngine()
        logger.info("Shared word engine initialized")
    
    return _global_word_engine

def cleanup_shared_word_engine():
    """Clean up the global word engine."""
    global _global_word_engine
    
    if _global_word_engine is not None:
        logger.info("Cleaning up shared word engine...")
        _global_word_engine = None
        logger.info("Shared word engine cleanup completed") 