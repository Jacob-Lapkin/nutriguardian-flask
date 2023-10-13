import pymongo
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from configuration.configuration import Development, Production

from .routes.main_bp import main_bp
from flasgger import Swagger
from .utils.swagger.swagger_config import swagger_template

jwt = JWTManager()
swagger = Swagger(template=swagger_template)
def create_app(config_class=Development):
    """
    Function used for creating the app instance of the flask api

    Params:
        config_class: class -> the class used for configuration imported from config file
    Returns:
        app: object -> return the app object initialzed from the Flask class
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB client
    app.db = pymongo.MongoClient(app.config['MONGO_URI']).nutriguardian
    version = app.config['VERSION']
    app.register_blueprint(main_bp, url_prefix=f"/api/{version}")

    jwt.init_app(app)  
    swagger.init_app(app)

    @app.route('/test', methods=["POST"])
    def test():
        return jsonify({"message":"test route"})

    return app