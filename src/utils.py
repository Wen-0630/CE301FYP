import requests
import os
from datetime import datetime
import time
import logging
import websocket
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def get_stock_data(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data


def get_crypto_data():
    try:
        url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&x_cg_demo_api_key=CG-1PFuk2DsTNsYUoWvgaqaubCA'
        response = requests.get(url)
        
        if response.status_code == 200:
            return format_crypto_data(response.json())
        else:
            logging.error("Failed to fetch crypto data: %s", response.status_code)
            return []
    except requests.RequestException as e:
        logging.error("Request failed: %s", e)
        return []


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
            'name': crypto['name'],
            'current_price': crypto['current_price'],
            'market_cap': crypto['market_cap'],
            'total_volume': crypto['total_volume'],
            'price_change_percentage_24h': crypto['price_change_percentage_24h']
        })
    return formatted_data


def get_formatted_stock_data(symbol):
    data = get_stock_data(symbol)
    return format_stock_data(data)

def get_formatted_crypto_data(crypto_list):
    data = get_crypto_data(crypto_list)
    return format_crypto_data(data)

def get_historical_crypto_data(crypto_list, start_date, end_date, hourly_mode=False):
    historical_prices = {}

    for crypto in crypto_list:
        # Set interval to 'hourly' for 24-hour mode only when supported by API
        interval = 'hourly' if hourly_mode else 'daily'
        
        # Build the API URL with the interval only if required
        url = (f'https://api.coingecko.com/api/v3/coins/{crypto.lower()}/market_chart/range'
               f'?vs_currency=usd&from={int(start_date.timestamp())}&to={int(end_date.timestamp())}'
               + (f'&interval={interval}' if hourly_mode else ''))

        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if 'prices' key is available in the response
            if 'prices' in data:
                # Format prices with the appropriate time format
                historical_prices[crypto.lower()] = {
                    datetime.utcfromtimestamp(item[0] / 1000).strftime(
                        '%Y-%m-%d %H:%M' if hourly_mode else '%Y-%m-%d'
                    ): item[1] for item in data['prices']
                }
            else:
                raise KeyError(f"'prices' not found for crypto {crypto}")
        else:
            raise Exception(f"Failed to fetch historical data for {crypto}: {response.status_code}")

    return historical_prices