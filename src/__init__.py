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
from src.notifications import Notification
from src.other_assets import other_assets
from src.other_liabilities import other_liabilities

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
    app.register_blueprint(other_assets, url_prefix='/')
    app.register_blueprint(other_liabilities, url_prefix='/')
    

    app.jinja_env.filters['format_currency'] = format_currency

    print("Connected to MongoDB Atlas successfully")
    # Set logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG)

    def format_currency_with_decimals(value):
        return "{:,.2f}".format(value)
    
    app.jinja_env.filters['currency_with_decimals'] = format_currency_with_decimals

    @app.context_processor
    def inject_notifications():
        notifications = []
        if 'user_id' in session:
            user_id = session['user_id']
            notifications = Notification.get_active_notifications(user_id)
        return dict(notifications=notifications)

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

    app.jinja_env.filters['format_with_commas'] = format_with_commas

    app.jinja_env.filters['format_balance'] = format_balance

    return app

def format_currency(value):
    return "{:,.0f}".format(value)

def format_with_commas(value):
    return "{:,.2f}".format(value)

def format_balance(value):
    """
    Custom filter to format numbers in 'k' for thousands and display normally for values below 1000.
    """
    if value >= 1000:
        # Format the value to 'k', rounded to 1 decimal place
        return f"{value / 1000:.1f}k"
    return f"{value:.0f}"