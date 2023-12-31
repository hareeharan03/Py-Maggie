# # unique_session_id.py
# import uuid

# # Initialize a variable to store the unique ID
# stored_unique_id = str(uuid.uuid4())

# # Define the unique_session_id function
# def unique_session_id():
#     return stored_unique_id

import uuid
from datetime import datetime

# Initialize a variable to store the unique ID
stored_unique_id = str(uuid.uuid4())

# Define the unique_session_id function
def unique_session_id():
    current_time = datetime.now()
    seconds = current_time.strftime("%S")
    minutes = current_time.strftime("%M")
    return f"{stored_unique_id}_{minutes}{seconds}"
