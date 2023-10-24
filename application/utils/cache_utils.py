from flask import current_app
import time
from flask import session
from flask_caching import Cache
import pandas as pd

from application.utils.logger import configure_logger

logger = configure_logger()

from application import create_app

from .cache import cache

def update_csv_file(df_name: str, df: pd.DataFrame, session=session) -> None:
    """Store the DataFrame in cache and raise an error if not stored."""

    dataframe_name = f"{df_name}_{session['session_id']}"
    cache.set(dataframe_name, df)
    # session['timestamp']= time.time()  # Update the timestamp
    cache.set('timestamp',(time.time()))

    # Check if the DataFrame is stored in the cache
    if cache.get(dataframe_name) is None:
        raise ValueError("DataFrame not stored in cache. Failed to update.")

    # Add dataframe_name to dataframes_saved_in_cache list in the session if not already present
    if 'dataframes_saved_in_cache' not in session:
        session['dataframes_saved_in_cache'] = []

    if dataframe_name not in session['dataframes_saved_in_cache']:
        session['dataframes_saved_in_cache'].append(dataframe_name)

def getting_csv(df_name: str,session=session) -> pd.DataFrame:
    """Retrieve the DataFrame from cache and return it."""
    
    dataframe_name = f"{df_name}_{session['session_id']}"
    retrieved_df = cache.get(dataframe_name)

    if retrieved_df is None:
        raise ValueError(f"DataFrame '{dataframe_name}' not found in cache.")

    return retrieved_df

# View cached keys and values
def view_cache():
    cached_keys = cache.cache._cache.keys()  # Get all cached keys
    return cached_keys

def clear_inactive_cache():
    while True:
        time.sleep(100000)  # Sleep for 5 minutes
        current_time = time.time()
        timestamp = cache.get('timestamp')
        print('-----------------------------------------------------',timestamp)
        if timestamp is not None and current_time - timestamp > 100000:
            logger.info('files stored in cache before clearing the cache data {}'.format(view_cache()))
            cache.clear()
            # session.clear()
            logger.info('files stoed in cache after clearing the cache data {}'.format(view_cache()))
            print('-----------------------------------------------------',timestamp)

def clear_inactive_cache_immediate():    
    logger.info('Currently running the clear_inactive_cache_immediate and clearing the cache and session')
    cache.clear()
    session.clear()