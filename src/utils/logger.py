"""
Logging configuration for the keyword research pipeline
"""
import logging
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/keyword_research.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)