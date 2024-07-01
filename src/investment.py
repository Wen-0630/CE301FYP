# src/investment.py
from flask import Blueprint, render_template, session, redirect, url_for, current_app
from bson.objectid import ObjectId
from .utils import get_stock_data, get_crypto_data

investment = Blueprint('investment', __name__, template_folder='templates')

@investment.route('/markets')
def markets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Define a dictionary of stock symbols to company names
    stock_symbols = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corp.'
    }
    
    stocks = {}
    for symbol, name in stock_symbols.items():
        data = get_stock_data(symbol)
        stocks[symbol] = {
            'name': name,
            'data': data
        }

    # Fetch crypto data for multiple cryptocurrencies
    crypto_list = ['bitcoin', 'ethereum', 'litecoin']  # Example crypto names
    crypto_data = get_crypto_data(crypto_list)

    # Process and store data in MongoDB
    user_id = session['user_id']
    current_app.mongo.db.markets.update_one(
        {'userId': ObjectId(user_id)},
        {"$set": {'stocks': stocks, 'crypto': crypto_data}},
        upsert=True
    )

    return render_template('markets.html', stocks=stocks, crypto_data=crypto_data)

@investment.route('/holdings')
def holdings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    holdings = current_app.mongo.db.holdings.find_one({'userId': ObjectId(user_id)})

    return render_template('holdings.html', holdings=holdings)
