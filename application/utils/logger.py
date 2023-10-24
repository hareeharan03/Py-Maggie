import logging
import uuid
from logging import FileHandler
from application.utils.unique_session import unique_session_id

unique_id = unique_session_id()

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


# azure logger---------------------------------------------------------------------------------------------

import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Azure Blob Storage connection details
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER = "logs"

def configure_logger():
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        unique_id = unique_session_id()
        log_filename = f"{unique_id}.log"

        # Create a BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

        # Create a container for your log files if it doesn't exist
        container_name = AZURE_BLOB_CONTAINER
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            container_client.create_container()

        # Create a BlobClient for the log file
        blob_client = container_client.get_blob_client(log_filename)

        if not blob_client.exists():
            # Create the blob with the initial log entry
            initial_log_entry = formatter.format(logging.LogRecord('root', logging.INFO, '', 0, 'Initial log entry', (), None, None)) + '\n'
            blob_client.upload_blob(initial_log_entry, overwrite=False)

        # Create a custom log handler to write directly to Azure Blob Storage
        class AzureBlobLogHandler(logging.Handler):
            def emit(self, record):
                log_entry = self.format(record) + '\n'

                # Append the log entry to the existing blob content
                with blob_client as blob:
                    current_content = blob.download_blob()
                    log_content = current_content.readall().decode('utf-8')
                    updated_content = log_content + log_entry
                    blob.upload_blob(updated_content, overwrite=True)

        azure_blob_handler = AzureBlobLogHandler()
        azure_blob_handler.setFormatter(formatter)
        logger.addHandler(azure_blob_handler)

    return logger

