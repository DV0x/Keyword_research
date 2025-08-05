"""
File I/O operations for the keyword research pipeline
"""
import json
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def initialize_directories():
    """Create necessary directories"""
    Path("data").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    logger.info("📁 Directories initialized")


def save_csv(df: pd.DataFrame, filename: str, description: str = "data"):
    """Save DataFrame to CSV with logging"""
    df.to_csv(filename, index=False)
    logger.info(f"💾 {description} saved to {filename}")


def save_json(data: dict, filename: str, description: str = "data"):
    """Save dictionary to JSON with logging"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"💾 {description} saved to {filename}")


def save_text_list(items: list, filename: str, description: str = "data"):
    """Save list of items to text file with logging"""
    with open(filename, 'w') as f:
        for item in items:
            f.write(f"{item}\n")
    logger.info(f"💾 {description} saved to {filename}")