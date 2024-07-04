# src/investment.py
from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, jsonify
from bson.objectid import ObjectId
from .utils import get_stock_data, get_crypto_data, get_formatted_crypto_data, get_formatted_stock_data
from datetime import datetime
import pytz

investment = Blueprint('investment', __name__, template_folder='templates')

def convert_to_singapore_time(timestamp):
    # Convert timestamp to Singapore time
    utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    singapore_time = utc_time.astimezone(pytz.timezone('Asia/Singapore'))
    return singapore_time.strftime("%Y-%m-%d %H:%M:%S")

@investment.route('/update_data')
def update_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    stock_symbols = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corp.'
    }

    stocks = {}
    for symbol, name in stock_symbols.items():
        data = get_formatted_stock_data(symbol)
        if data:
            latest_timestamp = sorted(data.keys())[-1]
            latest_data = data[latest_timestamp]
            latest_timestamp_sg = convert_to_singapore_time(latest_timestamp)
            stocks[symbol] = {
                'name': name,
                'latest_date': latest_timestamp_sg,
                'latest_close': latest_data['close'],
                'data': {convert_to_singapore_time(ts): val for ts, val in data.items()}
            }

    crypto_list = ['bitcoin', 'ethereum', 'litecoin']
    crypto_data = get_formatted_crypto_data(crypto_list)

    user_id = session['user_id']
    current_app.mongo.db.markets.update_one(
        {'userId': ObjectId(user_id)},
        {"$set": {'stocks': stocks, 'crypto': crypto_data}},
        upsert=True
    )

    return "Data updated successfully"

@investment.route('/markets')
def markets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user_data = current_app.mongo.db.markets.find_one({'userId': ObjectId(user_id)})

    if user_data:
        stocks = user_data.get('stocks', {})
        crypto_data = user_data.get('crypto', [])
    else:
        stocks = {}
        crypto_data = []

    return render_template('markets.html', stocks=stocks, crypto_data=crypto_data)

@investment.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    data = request.get_json()
    transaction_type = data['type']
    asset = data['asset']
    date = data['date']
    time = data['time']
    buy_price = float(data['buyPrice'])
    amount_bought = float(data['amountBought'])
    transaction_fee = float(data.get('transactionFee', 0))
    deduct_cash = "Yes" if data['deductCash'] else "No"

    user_id = session['user_id']

    # Convert date and time to datetime object
    datetime_str = f"{date} {time}"
    transaction_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    # Calculate quantity
    quantity = amount_bought / buy_price

    holding = {
        'userId': ObjectId(user_id),
        'asset': asset,
        'datetime': transaction_datetime,
        'buy_price': buy_price,
        'amount_bought': amount_bought,
        'quantity': quantity,
        'transaction_fee': transaction_fee,
        'deduct_cash': deduct_cash,
        'type': transaction_type  # Add type to the holding
    }

    if transaction_type == 'stock':
        current_app.mongo.db.stock_holdings.insert_one(holding)
    elif transaction_type == 'crypto':
        current_app.mongo.db.crypto_holdings.insert_one(holding)

    return jsonify({'success': True})


@investment.route('/holdings')
def holdings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    # Fetch stock and crypto holdings separately
    stock_holdings = list(current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)}))
    crypto_holdings = list(current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))
    
    # Fetch and format crypto data
    crypto_list = ['bitcoin', 'ethereum', 'litecoin']
    crypto_data = get_formatted_crypto_data(crypto_list)
    
    # Create a dictionary to map crypto IDs to current prices
    current_prices = {crypto['id']: crypto['current_price'] for crypto in crypto_data}
    
    # Calculate profit/loss for crypto holdings
    for holding in crypto_holdings:
        current_price = current_prices.get(holding['asset'].lower())
        if current_price:
            holding['profit_loss'] = (current_price - holding['buy_price']) * holding['quantity']
            current_app.mongo.db.crypto_holdings.update_one(
                {'_id': holding['_id']},
                {'$set': {'profit_loss': holding['profit_loss']}}
            )
        else:
            holding['profit_loss'] = 0  # Initialize profit_loss to 0 if current price is not available

    return render_template('holdings.html', holdings={'stock_holdings': stock_holdings, 'crypto_holdings': crypto_holdings}, crypto_data=crypto_data)




def calculate_total_investment_profit_loss(user_id):
    stock_holdings = current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)})
    crypto_holdings = current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)})

    total_profit_loss = 0

    # Sum profit/loss for stock holdings
    for holding in stock_holdings:
        current_price = get_stock_data(holding['asset'])['Time Series (60min)'][holding['datetime'].strftime("%Y-%m-%d %H:%M:%S")]['4. close']
        holding['profit_loss'] = (current_price - holding['buy_price']) * holding['quantity']
        total_profit_loss += holding['profit_loss']

    # Sum profit/loss for crypto holdings
    for holding in crypto_holdings:
        crypto_list = [holding['asset']]
        crypto_data = get_formatted_crypto_data(crypto_list)
        current_price = crypto_data[0]['current_price']
        holding['profit_loss'] = (current_price - holding['buy_price']) * holding['quantity']
        total_profit_loss += holding['profit_loss']

    return total_profit_loss
