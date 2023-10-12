import os

SECRET_KEY = os.environ['SECRET_KEY']
DATABASE_URL = os.environ["DATABASE_URL"]

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = False
    DATABASE_URL = os.environ["DATABASE_URL"]

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = os.environ["DATABASE_URL"]

class TestingConfig(Config):
    TESTING = True
