import pytest
from application.utils.database_utils import connect_to_database
from application.utils.report_utils import output_info
from application.utils.report_utils import terminal

# Test the database connection
def test_connect_to_database(mock_database_connection):
    assert mock_database_connection is not None

# Import necessary modules and functions

# Test the insertion behavior of the output_info function
def test_output_info_insertion(mock_database_connection):
    # Set up a sample session and input data
    mock_session = {'session_id': '123azafacdzcad4567lkn22318', 'session_started_timestamp': 123456789}
    input_data = 'Sample input data for testing'

    output_string_col = mock_database_connection['mock_databases']

    # Call the output_info function with the mock database connection
    output_info(input_data, mock_session['session_id'], mock_session['session_started_timestamp'], output_string_col)

    # Retrieve the inserted document from the mock database
    result = output_string_col.find_one({'_id': mock_session['session_id']}, {'report_data': 1})

    # Assert that the document exists and contains the expected data
    assert result is not None
    assert result.get('report_data') == input_data


# Test the updating behavior of the output_info function
def test_output_info_updating(mock_database_connection):
    # Set up a sample session and input data
    mock_session = {'session_id': '123azcdzcadffff4567lkn22318', 'session_started_timestamp': 123456789}
    input_data = 'Sample input data for testing'

    output_string_col = mock_database_connection['mock_databases']

    # Call the output_info function with the mock database connection for the first input
    output_info(input_data, mock_session['session_id'], mock_session['session_started_timestamp'], output_string_col)

    input_data_2 = 'the insertion and updation'

    # Call the output_info function again to update the document
    output_info(input_data_2, mock_session['session_id'], mock_session['session_started_timestamp'], output_string_col)

    # Retrieve the updated document from the mock database
    result = output_string_col.find_one({'_id': mock_session['session_id']}, {'report_data': 1})

    # Assert that the document exists and contains the updated data
    assert result is not None
    expected_data = f'''{input_data}<br><br>{terminal}{input_data_2}'''
    print("+++++++++++++++++++++++++++++++++++++++++",result.get('report_data'))
    assert result.get('report_data') == expected_data



# # Test the get_report_data function
# def test_get_report_data(mock_database_connection):
#     # Set up a sample session and input data
#     session = {'session_id': '12345', 'session_started_timestamp': 123456789}
#     input_data = 'Sample input data'

#     # Insert a sample document into the mock database
#     mock_database_connection.insert_one({'_id': session['session_id'], 'started_time': session['session_started_timestamp'], 'report_data': input_data})

#     # Call the get_report_data function with the mock database connection
#     result = get_report_data(mock_database_connection, session)

#     # Assert that the retrieved data matches the inserted data
#     assert result == input_data

