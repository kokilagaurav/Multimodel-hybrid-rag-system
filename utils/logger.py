"""
logger: 
    1. log messages
    2. log errors
    3. log warnings
"""

import logging
from pathlib import Path
from datetime import datetime


class LoggerConfig:

    BASE_DIR = Path(__file__).resolve().parent.parent

    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


logging.basicConfig(
    level=logging.INFO,
    format=LoggerConfig.LOG_FORMAT,
    handlers=[
        logging.FileHandler(LoggerConfig.LOG_FILE),
        logging.StreamHandler()
    ]
)


def get_logger(name: str):
    return logging.getLogger(name)