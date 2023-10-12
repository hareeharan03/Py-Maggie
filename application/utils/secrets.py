from dotenv import load_dotenv

import os

load_dotenv()

def get_secret_key():
    secret_key = os.getenv("SECRET_KEY")
    return str(secret_key)

# Call the function to get the secret key and then print it
print(get_secret_key())

def get_database_URL():
    database_URL=os.getenv("DATABASE_URL")
    return str(database_URL)

print(get_database_URL())



