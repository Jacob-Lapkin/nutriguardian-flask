from flask import Flask
import pymongo
from ..configuration.configuration import Development, Production
from routes import main_bp

def create_app(config_class=Development):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB client
    app.db = pymongo.MongoClient(app.config['MONGO_URI']).db

    app.register_blueprint(main_bp)

    return app