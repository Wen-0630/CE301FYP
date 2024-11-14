# src/investment.py
from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, jsonify
from bson.objectid import ObjectId
from .utils import  get_crypto_data, get_historical_crypto_data
from datetime import datetime, timedelta
import pytz
import time
import websocket
import threading
import json
from math import isnan


investment = Blueprint('investment', __name__, template_folder='templates')

# CACHE = {}
# CACHE_TIMEOUT = 300  # 5 minutes in seconds

# def get_cached_data(key):
#     current_time = time.time()
#     if key in CACHE and current_time - CACHE[key]['timestamp'] < CACHE_TIMEOUT:
#         return CACHE[key]['data']
#     return None

# def set_cached_data(key, data):
#     CACHE[key] = {
#         'timestamp': time.time(),
#         'data': data
#     }

# def convert_to_singapore_time(timestamp):
#     # Convert timestamp to Singapore time
#     utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
#     utc_time = utc_time.replace(tzinfo=pytz.utc)
#     singapore_time = utc_time.astimezone(pytz.timezone('Asia/Singapore'))
#     return singapore_time.strftime("%Y-%m-%d %H:%M:%S")

# @investment.route('/update_data')
# def update_data():
#     if 'user_id' not in session:
#         return redirect(url_for('auth.login'))
    
#     cache_key = 'market_data'
#     cached_data = get_cached_data(cache_key)
#     if cached_data:
#         return jsonify({'success': True, 'message': 'Data loaded from cache'})

#     stock_symbols = {
#         'AAPL': 'Apple Inc.',
#         'GOOGL': 'Alphabet Inc.',
#         'MSFT': 'Microsoft Corp.'
#     }

#     stocks = {}
#     for symbol, name in stock_symbols.items():
#         data = get_formatted_stock_data(symbol)
#         if data:
#             latest_timestamp = sorted(data.keys())[-1]
#             latest_data = data[latest_timestamp]
#             latest_timestamp_sg = convert_to_singapore_time(latest_timestamp)
#             stocks[symbol] = {
#                 'name': name,
#                 'latest_date': latest_timestamp_sg,
#                 'latest_close': latest_data['close'],
#                 'data': {convert_to_singapore_time(ts): val for ts, val in data.items()}
#             }

#     crypto_list = ['bitcoin', 'ethereum', 'litecoin']
#     crypto_data = get_formatted_crypto_data(crypto_list)

    # user_id = session['user_id']    
    # current_app.mongo.db.markets.update_one(
    #     {'userId': ObjectId(user_id)},
    #     {"$set": {'stocks': stocks, 'crypto': crypto_data}},
    #     upsert=True
    # )

    # set_cached_data(cache_key, {'stocks': stocks, 'crypto': crypto_data})

    # return "Data updated successfully"

def start_websocket(app):
    def on_message(ws, message):
        data = json.loads(message)
        
        if data['type'] == 'trade':
            with app.app_context():  # Push application context here
                for trade in data['data']:
                    symbol = trade['s']
                    last_price = trade['p']
                    volume = trade['v']
                    timestamp = datetime.fromtimestamp(trade['t'] / 1000)  # Convert ms to seconds
                    
                    # Store in MongoDB
                    current_app.mongo.db.stocks.update_one(
                        {'symbol': symbol},
                        {
                            '$set': {
                                'last_price': last_price,
                                'volume': volume,
                                'timestamp': timestamp
                            }
                        },
                        upsert=True
                    )
    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("### WebSocket closed ###")
        print(f"Code: {close_status_code}, Message: {close_msg}")
        time.sleep(5)  # Wait before reconnecting
        start_websocket(app)  # Attempt reconnection


    def on_open(ws):
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'BRK.B', 'JPM', 'V',
            'JNJ', 'WMT', 'PG', 'UNH', 'MA', 'NVDA', 'HD', 'DIS', 'BAC', 'VZ', 'KO',
            'PFE', 'NFLX', 'INTC', 'CMCSA', 'PEP', 'CSCO', 'T', 'XOM', 'BA', 'ORCL',
            'C', 'ABBV', 'MCD', 'ABT', 'NKE', 'LLY', 'CRM', 'ACN', 'DHR', 'MDT',
            'QCOM', 'TXN', 'HON', 'MRK', 'IBM', 'RTX', 'GS', 'CAT', 'MMM', 'GE'
        ]
        for symbol in symbols:
            ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

    ws = websocket.WebSocketApp(
        "wss://ws.finnhub.io?token=csgj1bpr01qldu0cq0ugcsgj1bpr01qldu0cq0v0",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

# Start WebSocket in a new thread to keep it running alongside the Flask app
def start_websocket_thread(app):
    threading.Thread(target=start_websocket, args=(app,), daemon=True).start()

@investment.route('/markets')
def markets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    stocks = list(current_app.mongo.db.stocks.find())
    crypto_data = get_crypto_data()  # Fetch crypto data directly from the API

    # print("Stock Data:", stocks)  # Debugging line to check stock data
    # print("Crypto Data:", crypto_data)  # Debugging line to check crypto dat

    return render_template('markets.html', stocks=stocks, crypto_data=crypto_data)

# @investment.route('/add_transaction', methods=['POST'])
# def add_transaction():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'User not logged in'}), 401

#     data = request.get_json()
#     transaction_type = data['type']
#     asset = data['asset']
#     date = data['date']
#     time = data['time']
#     buy_price = float(data['buyPrice'])
#     amount_bought = float(data['amountBought'])
#     transaction_fee = float(data.get('transactionFee' or 0))
#     deduct_cash = "Yes" if data['deductCash'] else "No"

#     user_id = session['user_id']

#     # Convert date and time to datetime object
#     datetime_str = f"{date} {time}"
#     transaction_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

#     # Calculate quantity
#     quantity = amount_bought / buy_price

#     holding = {
#         'userId': ObjectId(user_id),
#         'asset': asset,
#         'datetime': transaction_datetime,
#         'buy_price': buy_price,
#         'amount_bought': amount_bought,
#         'quantity': quantity,
#         'transaction_fee': transaction_fee,
#         'deduct_cash': deduct_cash,
#         'type': transaction_type  # Add type to the holding
#     }

#     if transaction_type == 'stock':
#         current_app.mongo.db.stock_holdings.insert_one(holding)
#     elif transaction_type == 'crypto':
#         current_app.mongo.db.crypto_holdings.insert_one(holding)

#     return jsonify({'success': True})

@investment.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    try:
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
        datetime_str = f"{date} {time}"
        transaction_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
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
            'type': transaction_type
        }

        if transaction_type == 'stock':
            current_app.mongo.db.stock_holdings.insert_one(holding)
        elif transaction_type == 'crypto':
            current_app.mongo.db.crypto_holdings.insert_one(holding)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@investment.route('/holdings')
def holdings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    # Fetch stock and crypto holdings separately
    stock_holdings = list(current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)}))
    crypto_holdings = list(current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))
    
    # Fetch and format crypto data

    crypto_data = get_crypto_data()
    print("Crypto Data:", crypto_data)
    stocks_data = list(current_app.mongo.db.stocks.find())

    # Create a dictionary to map crypto IDs to current prices
    current_prices = {crypto['name'].title(): crypto['current_price'] for crypto in crypto_data}
    print("Current Prices:", current_prices) 

    stock_current_prices = {stock['symbol']: stock['last_price'] for stock in stocks_data}

    
    # Calculate profit/loss for crypto holdings
    for holding in crypto_holdings:
        current_price = current_prices.get(holding['asset'].title())
        if current_price:
            holding['profit_loss'] = (current_price - holding['buy_price']) * holding['quantity']
            current_app.mongo.db.crypto_holdings.update_one(
                {'_id': holding['_id']},
                {'$set': {'profit_loss': holding['profit_loss']}}
            )

        else:
            holding['profit_loss'] = 0  # Initialize profit_loss to 0 if current price is not available

        # Calculate profit/loss for crypto holdings
    for holding in stock_holdings:
        stock_current_price = stock_current_prices.get(holding['asset'].upper())
        if stock_current_price:
            holding['profit_loss'] = (stock_current_price - holding['buy_price']) * holding['quantity']
            current_app.mongo.db.stock_holdings.update_one(
                {'_id': holding['_id']},
                {'$set': {'profit_loss': holding['profit_loss']}}
            )
        else:
            holding['profit_loss'] = 0 

    return render_template('holdings.html', holdings={'stock_holdings': stock_holdings, 'crypto_holdings': crypto_holdings}, stocks_data = stocks_data, crypto_data=crypto_data)




def calculate_total_investment_profit_loss(user_id):
    # Fetch stock and crypto holdings from the database
    stock_holdings = current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)})
    crypto_holdings = current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)})

    total_profit_loss = 0

    # Sum the existing profit/loss for stock holdings
    for holding in stock_holdings:
        total_profit_loss += holding.get('profit_loss', 0)

    # Sum the existing profit/loss for crypto holdings
    for holding in crypto_holdings:
        total_profit_loss += holding.get('profit_loss', 0)

    return total_profit_loss


@investment.route('/delete_stock_holding', methods=['POST'])
def delete_stock_holding():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    data = request.get_json()
    holding_id = data['holdingId']

    result = current_app.mongo.db.stock_holdings.delete_one({'_id': ObjectId(holding_id)})
    if result.deleted_count == 1:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete stock holding'})


@investment.route('/delete_crypto_holding', methods=['POST'])
def delete_crypto_holding():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    data = request.get_json()
    holding_id = data['holdingId']

    result = current_app.mongo.db.crypto_holdings.delete_one({'_id': ObjectId(holding_id)})
    if result.deleted_count == 1:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete crypto holding'})

def parse_date(date_str):
    """Parse date string in either 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format."""
    try:
        # Try parsing as full date-time if available
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        # Fallback to date-only format
        return datetime.strptime(date_str, '%Y-%m-%d')

@investment.route('/api/profit_loss_over_time', methods=['GET'])
def profit_loss_over_time():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Get start_date and end_date from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    hourly_mode = request.args.get('hourly_mode', 'false').lower() == 'true'

    try:
        # Parse dates according to the expected format
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    try:
        # Fetch user holdings and handle data retrieval accordingly
        crypto_holdings = list(current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))
        crypto_list = [holding['asset'] for holding in crypto_holdings]

        # Fetch historical data using the hourly mode if specified
        historical_prices = get_historical_crypto_data(crypto_list, start_date, end_date, hourly_mode=hourly_mode)

        # Calculate profit/loss for each holding and format the response
        profit_loss_data = []
        for holding in crypto_holdings:
            asset = holding['asset'].lower()
            buy_price = holding['buy_price']
            quantity = holding['quantity']
            
            for date, price in historical_prices.get(asset, {}).items():
                profit_loss = (price - buy_price) * quantity
                profit_loss_data.append({
                    'date': date,
                    'profit_loss': profit_loss
                })

        # Sort data by date
        profit_loss_data.sort(key=lambda x: x['date'])

        return jsonify(profit_loss_data)

    except KeyError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profit/loss data'}), 500
    
@investment.route('/api/holdings_over_time', methods=['GET'])
def holdings_over_time():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Set up date range for the last six months, capturing month start dates
    end_date = datetime.now()
    labels = [(end_date - timedelta(days=i * 30)).strftime('%Y-%m') for i in range(5, -1, -1)]
    month_starts = [(end_date.replace(day=1) - timedelta(days=i * 30)).replace(day=1) for i in range(5, -1, -1)]

    # Initialize data structure for cumulative stock and crypto amounts per month
    monthly_holdings = {label: {'stock_total': 0, 'crypto_total': 0} for label in labels}

    try:
        # Get stock and crypto holdings from MongoDB
        stock_holdings = list(current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)}))
        crypto_holdings = list(current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))

        # Calculate cumulative holdings by month
        def update_cumulative_holdings(holdings, holding_type):
            # Sort holdings by date to make sure we handle them chronologically
            holdings.sort(key=lambda h: h['datetime'])
            cumulative_total = 0

            for start, label in zip(month_starts, labels):
                # Add holdings purchased before or in this month
                while holdings and holdings[0]['datetime'] < start:
                    cumulative_total += holdings.pop(0)['amount_bought']
                
                monthly_holdings[label][f'{holding_type}_total'] = cumulative_total

        # Update cumulative holdings for stocks and crypto
        update_cumulative_holdings(stock_holdings, 'stock')
        update_cumulative_holdings(crypto_holdings, 'crypto')

        # Prepare data for the chart
        data = {
            'months': labels,
            'stock_totals': [monthly_holdings[month]['stock_total'] for month in labels],
            'crypto_totals': [monthly_holdings[month]['crypto_total'] for month in labels],
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@investment.route('/api/current_holdings_totals', methods=['GET'])
def current_holdings_totals():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    stock_total = sum(holding['amount_bought'] for holding in current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)}))
    crypto_total = sum(holding['amount_bought'] for holding in current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))

    return jsonify({'stock_total': stock_total, 'crypto_total': crypto_total})

@investment.route('/api/get_holding/<holding_type>/<holding_id>', methods=['GET'])
def get_holding(holding_type, holding_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        # Determine the collection based on the holding type
        if holding_type == 'stock':
            collection = current_app.mongo.db.stock_holdings
        elif holding_type == 'crypto':
            collection = current_app.mongo.db.crypto_holdings
        else:
            return jsonify({'error': 'Invalid holding type'}), 400

        # Fetch the holding document
        holding = collection.find_one({'_id': ObjectId(holding_id), 'userId': ObjectId(user_id)})
        if not holding:
            return jsonify({'error': 'Holding not found'}), 404

        # Convert ObjectId fields to string for JSON serialization
        holding['_id'] = str(holding['_id'])
        holding['userId'] = str(holding['userId'])

        # Check for NaN in numeric fields and replace with 0
        holding['buy_price'] = holding.get('buy_price') or 0
        holding['transaction_fee'] = holding.get('transaction_fee') or 0
        if isnan(holding['buy_price']):
            holding['buy_price'] = 0
        if isnan(holding['transaction_fee']):
            holding['transaction_fee'] = 0

        return jsonify(holding), 200

    except Exception as e:
        print(f"Error fetching holding: {e}")  # Print the error for debugging
        return jsonify({'error': 'Internal server error'}), 500



@investment.route('/api/update_holding', methods=['POST'])
def update_holding():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()
    holding_id = data['holdingId']
    holding_type = data['holdingType']
    update_fields = {
        'buy_price': float(data['buy_price']),
        'quantity': float(data['quantity']),
        'amount_bought': float(data['amount_bought']),
        'transaction_fee': float(data['transaction_fee'])
    }

    collection = 'stock_holdings' if holding_type == 'stock' else 'crypto_holdings'
    result = current_app.mongo.db[collection].update_one(
        {'_id': ObjectId(holding_id)},
        {'$set': update_fields}
    )

    if result.modified_count == 1:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update holding'})

