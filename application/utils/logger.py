import logging
import uuid
from logging import FileHandler
from application.utils.unique_session import unique_session_id

# #configuring logger

# def configure_logger():
#     logger = logging.getLogger(__name__)
#     logger.setLevel(logging.INFO)

#     # Check for multiple handler additions and ensure only one file handler is added
#     if not logger.hasHandlers():
#         formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

#         unique_id = unique_session_id()
#         file_handler = logging.FileHandler(f"logger_{unique_id}.log")
#         file_handler.setFormatter(formatter)

#         logger.addHandler(file_handler)
#         # print("inside handler--============================+++++++++++++++++++++++++++++++++++++++")

#     return logger


import logging
import uuid
from pymongo import MongoClient
from config import DATABASE_URL

# Initialize MongoDB connection
client = MongoClient(str(DATABASE_URL))
db = client['main_database']
log_collection = db["log_collection_name"]

# Configure logger
def configure_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Check for multiple handler additions and ensure only one handler is added
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        # Create a custom logging handler
        class MongoDBHandler(logging.Handler):
            def emit(self, record):
                log_entry = {
                    "level": record.levelname,
                    "message": self.format(record),
                    "timestamp": record.created
                }
                log_collection.insert_one(log_entry)

        # Create a custom logging handler to write log messages to a file
        log_filename = "log_ksj.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)

        # Create the MongoDBHandler and set its formatter
        mongodb_handler = MongoDBHandler()
        mongodb_handler.setFormatter(formatter)

        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(mongodb_handler)

    return logger

