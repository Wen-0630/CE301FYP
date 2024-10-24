import requests
import os
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def get_stock_data(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_crypto_data(crypto_list):
    url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={",".join(crypto_list)}'
    
    while True:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))  # Default to 60 seconds if header is not present
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            response.raise_for_status()

    return None


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

def get_historical_crypto_data(crypto_list, start_date, end_date):
    url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={",".join(crypto_list)}&from={int(start_date.timestamp())}&to={int(end_date.timestamp())}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        historical_prices = {}
        
        for crypto in data:
            historical_prices[crypto['id']] = {
                item['timestamp']: item['price'] for item in crypto['prices']
            }
        
        return historical_prices
    else:
        raise Exception("Failed to fetch historical crypto data")
