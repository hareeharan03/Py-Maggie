import pytest
import pandas as pd
from application.utils.cache_utils import update_csv_file, getting_csv
from application.utils.cache import cache


def test_update_csv_file(app, client, clear_cache):
    with app.app_context():
        # Manually set the session_id in the session
        session = {'session_id': 'test_session_id'}

        # Define test data
        df_name = 'test_dataframe'
        df = pd.DataFrame({'col1': [1, 2, 3]})

        # Call the update_csv_file function
        update_csv_file(df_name, df, session=session)

        # Retrieve the data from the cache
        cached_df = getting_csv(df_name, session=session)

        # Check if the data is retrieved correctly
        assert cached_df is not None
        assert cached_df.equals(df)

        # Check if the timestamp is stored in the cache
        cached_timestamp = cache.get('timestamp')
        assert cached_timestamp is not None

def test_get_csv_not_in_cache(app, client, clear_cache):
    with app.app_context():
        # Manually set the session_id in the session
        session = {'session_id': 'test_session_id'}

        # Try to retrieve a DataFrame that is not in the cache
        df_name = 'non_existent_dataframe'
        with pytest.raises(ValueError, match="DataFrame 'non_existent_dataframe_test_session_id' not found in cache."):
            getting_csv(df_name, session=session)