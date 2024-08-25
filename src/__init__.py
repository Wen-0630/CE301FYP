from flask import Flask, g, session, current_app
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from src.auth import auth
from src.views import views
from src.transactions import transactions
from src.creditCard import credit_card
from src.loan import loan
from src.investment import investment
from src.cashFlow import cashflow_bp
import certifi
import logging
from bson.objectid import ObjectId
from src.savingGoals import savingGoals_bp
from src.budget import budget_bp


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
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(transactions, url_prefix='/')
    app.register_blueprint(credit_card, url_prefix='/')
    app.register_blueprint(loan, url_prefix='/')
    app.register_blueprint(investment, url_prefix='/')
    app.register_blueprint(cashflow_bp, url_prefix='/')
    app.register_blueprint(savingGoals_bp, url_prefix='/')
    app.register_blueprint(budget_bp, url_prefix='/')

    app.jinja_env.filters['format_currency'] = format_currency

    print("Connected to MongoDB Atlas successfully")
    # Set logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG)

    def format_currency_with_decimals(value):
        return "{:,.2f}".format(value)
    
    app.jinja_env.filters['currency_with_decimals'] = format_currency_with_decimals

    @app.before_request
    def before_request():
        g.user = None
        if 'user_id' in session:
            user_data = current_app.mongo.cx['CE-301'].users.find_one({"_id": ObjectId(session['user_id'])})
            if user_data:
                g.user = user_data

    @app.context_processor
    def inject_user():
        return dict(user=g.user)
    
    # In your main application setup file (e.g., app.py)

    def max_filter(value, default=0):
        return max(value, default)

    app.jinja_env.filters['max'] = max_filter

    @app.template_filter('min_value')
    def min_value_filter(a, b):
        return min(a, b)

    # Register the filter
    app.jinja_env.filters['min_value'] = min_value_filter


    return app

def format_currency(value):
    return "{:,.0f}".format(value)


