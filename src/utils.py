import requests
import os
from datetime import datetime

def get_stock_data(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_crypto_data(crypto_list):
    url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={",".join(crypto_list)}'
    response = requests.get(url)
    data = response.json()
    return data

def format_stock_data(data):
    if 'Time Series (60min)' not in data:
        return None

    formatted_data = {}
    for timestamp, values in data['Time Series (60min)'].items():
        formatted_data[timestamp] = {
            'open': values['1. open'],
            'high': values['2. high'],
            'low': values['3. low'],
            'close': values['4. close'],
            'volume': values['5. volume']
        }
    return formatted_data

def format_crypto_data(data):
    formatted_data = []
    for crypto in data:
        formatted_data.append({
            'id': crypto['id'],
            'symbol': crypto['symbol'],
            'name': crypto['name'],
            'current_price': crypto['current_price'],
            'market_cap': crypto['market_cap'],
            'total_volume': crypto['total_volume'],
            'high_24h': crypto['high_24h'],
            'low_24h': crypto['low_24h'],
            'price_change_24h': crypto['price_change_24h'],
            'price_change_percentage_24h': crypto['price_change_percentage_24h']
        })
    return formatted_data

def get_formatted_stock_data(symbol):
    data = get_stock_data(symbol)
    return format_stock_data(data)

def get_formatted_crypto_data(crypto_list):
    data = get_crypto_data(crypto_list)
    return format_crypto_data(data)
