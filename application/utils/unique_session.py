# unique_session_id.py
import uuid

# Initialize a variable to store the unique ID
stored_unique_id = str(uuid.uuid4())

# Define the unique_session_id function
def unique_session_id():
    return stored_unique_id
