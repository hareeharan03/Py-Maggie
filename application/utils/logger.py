import logging
import uuid
from logging import FileHandler

#configuring logger

def configure_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Check for multiple handler additions and ensure only one file handler is added
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        unique_id = str(uuid.uuid4())
        file_handler = logging.FileHandler(f"logger_{unique_id}.log")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        print("inside handler--============================+++++++++++++++++++++++++++++++++++++++")

    return logger
