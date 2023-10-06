from pymongo import MongoClient
from config import DATABASE_URL

def connect_to_database():
    client = MongoClient(str(DATABASE_URL))
    db = client['main_database']
    output_string_col = db['output_string']
    return output_string_col