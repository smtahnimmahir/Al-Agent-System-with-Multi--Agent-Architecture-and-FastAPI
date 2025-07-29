import logging
import sys
from typing import Optional
from app.core.config import get_settings

def setup_logging(log_level: Optional[str] = None):
    """Configure application logging"""
    settings = get_settings()
    level = getattr(logging, log_level or settings.log_level.upper())
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)