from flask import Flask
from config import SECRET_KEY
from application.utils.cache import cache

def create_app():

    app = Flask(__name__, static_folder='staticFiles')

    # Set the Flask app's SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY

    cache.init_app(app)

    from application.views.EDA.routes import EDA
    from application.views.data_preprocessing.routes import data_preprocessing
    from application.views.data_splitting.routes import data_splitting
    from application.views.file_download.routes import file_download
    from application.views.handler.routes import handler

    app.register_blueprint(handler)
    app.register_blueprint(EDA)
    app.register_blueprint(data_preprocessing)
    app.register_blueprint(data_splitting)
    app.register_blueprint(file_download)

    return app
