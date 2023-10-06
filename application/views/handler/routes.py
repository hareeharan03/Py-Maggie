from flask import Flask, render_template, Blueprint
import threading

#utils import
from application.utils.cache_utils import clear_inactive_cache

handler=Blueprint('handler',__name__, static_folder='application\staticFiles')

#Define the custom error handler
@handler.app_errorhandler(500)
def internal_server_error(error):
    # Log the error message
    # logger.error('Server Error: %s', (error))
    print(error)
    # Render the error page template with the error message
    return render_template('error_page.html', error=error), 500
    

@handler.before_app_request
def start_background_thread():
    print("Started")
    background_thread = threading.Thread(target=clear_inactive_cache)
    background_thread.daemon = True
    background_thread.start()