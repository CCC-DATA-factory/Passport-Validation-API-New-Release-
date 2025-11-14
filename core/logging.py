# core/logging.py

import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# ----------------------------
# 1️⃣ Create logs directory if not exists
# ----------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "passport_api.log")

# ----------------------------
# 2️⃣ Logger configuration
# ----------------------------
logger = logging.getLogger("passport_api")
logger.setLevel(logging.INFO)

# File handler (rotating)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)

def setup_logger():
    logger = logging.getLogger("passport_api")
    logger.setLevel(LOG_LEVEL)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


# ----------------------------
# 3️⃣ Usage
# ----------------------------
# from core.logging import logger
# logger.info("Message")
