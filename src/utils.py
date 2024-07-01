import requests
import os

def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={os.getenv("ALPHA_VANTAGE_API_KEY")}'
    response = requests.get(url)
    data = response.json()
    return data

def get_crypto_data(crypto_list):
    url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={",".join(crypto_list)}'
    response = requests.get(url)
    data = response.json()
    return data
