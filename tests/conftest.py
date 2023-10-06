import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Adjust the path as needed

from application.utils.cache import cache
from application.utils.logger import configure_logger

from application import create_app

# from app import app as flask_app  # Import your Flask app instance

import pytest
from mongomock import MongoClient
# from app import app  as mock_app# Import your Flask app factory function here

@pytest.fixture
def app():
    app = create_app()  # Adjust this according to your app setup

    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def clear_cache(app):
    yield  # This is where the test runs
    with app.app_context():
        cache.clear()


# Define a fixture to configure the logger
@pytest.fixture
def logger():
    return configure_logger()



# Fixture for setting up a clean mock database connection
@pytest.fixture(scope='function')
def mock_database_connection():
    # Set up the mock database connection
    mock_client = MongoClient()
    db = mock_client['mock_database']

    # Yield the mock database connection to the test
    yield db

    # Optionally, clean up any test data created during the test
    db.drop_collection('collection_name')
