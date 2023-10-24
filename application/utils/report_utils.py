from flask import session

from application.utils.database_utils import connect_to_database

from application.utils.logger import configure_logger
logger = configure_logger()

#connecting to the database
output_string_col = connect_to_database()

terminal='''<span class="Prompt__user">cody@ubuntu:</span>
            <span class="Prompt__location">~</span><span class="Prompt__dollar">$ </span>'''

def output_info(inp, id=None, time=None, output_string_col=output_string_col):
    try:
        # Use _id and _time if provided, otherwise use session values
        if id is None:
            id = session['session_id']
        if time is None:
            time = session['session_started_timestamp']

        # Check if the session ID exists in the output_string collection
        result = output_string_col.find_one({'_id': id, 'started_time': time})

        if result is None:
            # If no matching document exists, insert the session ID, time, and input string as a new document
            output_string_col.insert_one({'_id': id, 'started_time': time, 'report_data': inp})

        else:
            # If a matching document exists, append the input string to the existing report data
            report_data = str(result.get('report_data', '')) + '<br><br>' + terminal +str(inp)
            output_string_col.update_one({'_id': id, 'started_time': time}, {'$set': {'report_data': report_data}})

    except Exception as e:
        # Handle exceptions and log errors
        logger.error(f"Error in output_info({id}, {time}, {inp}): {str(e)}")

def get_report_data(id=None):
    try:
        # Use _id if provided, otherwise use session['session_id']
        if id is None:
            id = session.get('session_id')

        # Retrieve the report data for the specified _id from the output_string collection
        result = output_string_col.find_one({'_id': id}, {'report_data': 1})

        if result:
            # If a matching document exists, return the report data
            message = result.get('report_data')
            return message
        else:
            # If no matching document exists, return None
            return None
    except Exception as e:
        # Handle exceptions and log errors
        logger.error(f"Error in get_report_data({id}): {str(e)}")
        return None





# older version





# def output_info(inp):
#     # check if session ID already exists in the output_string collection
#     result = output_string_col.find_one({'_id': session['session_id'], 'started_time': session['session_started_timestamp']})
    
#     if result is None:
#         # if no matching document exists, insert the session ID and input string as a new document
#         output_string_col.insert_one({'_id': session['session_id'], 'started_time': session['session_started_timestamp'], 'report_data': inp})

#     else:
#         # if matching document exists, append the input string to the existing report data and update the CSV file
#         report_data = str(result['report_data']) + str('<br><br>') + str(inp)
#         output_string_col.update_one({'_id': session['session_id'], 'started_time': session['session_started_timestamp']}, {'$set': {'report_data': report_data}})



# def get_report_data():
#     # retrieve the report data for the session ID from the output_string collection
#     result = output_string_col.find_one({'_id': session['session_id']}, {'report_data': 1})
    
#     if result:
#         # if matching document exists, return the report data
#         message = result['report_data']
#         return message
#     else:
#         # if no matching document exists, return None
#         return None