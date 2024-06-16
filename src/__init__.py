from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from src.auth import auth
from src.views import views
from src.transactions import transactions
import certifi
import logging

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config['MONGO_TLS_CA_FILE'] = certifi.where()

    app.secret_key = os.getenv("SECRET_KEY")

    app.config['DEBUG'] = True  # Ensure debug mode is enabled
    
    mongo = PyMongo(app)
    app.mongo = mongo

    bcrypt = Bcrypt(app)  # Initialize Bcrypt with the Flask app
    app.bcrypt = bcrypt

    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(transactions, url_prefix='/transactions')

    print("Connected to MongoDB Atlas successfully")
    # Set logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG)
    
    
    return app
