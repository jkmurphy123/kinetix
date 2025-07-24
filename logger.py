import logging
import os

LOG_DIR = "logs"

def get_logger(name: str) -> logging.Logger:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    log_path = os.path.join(LOG_DIR, f"{name}.log")
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    logger.propagate = False  # Prevent duplicate logs

    return logger
