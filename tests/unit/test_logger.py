# from application.utils.logger import configure_logger
# import logging
# import os

# # Call configure_logger() to set up the logger before any tests are run
# logger = configure_logger()

# def test_log_file_creation():
#     # Get the log file path from the logger
#     log_file_path = logger.handlers[0].baseFilename

#     # Ensure the log file doesn't exist before running the Flask app
#     if os.path.exists(log_file_path):
#         os.remove(log_file_path)

#     # Simulate some logging
#     logger.info('This is a log message.')

#     # Check if the log file was created
#     assert os.path.exists(log_file_path)