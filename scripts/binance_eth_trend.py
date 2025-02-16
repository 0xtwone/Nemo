import requests
import json
from datetime import datetime


def fetch_candlestick_data(symbol, interval, limit=24):
    """
    Fetch candlestick data from Binance API for the given symbol and interval.
    :param symbol: Trading pair symbol, e.g. 'ETHUSDT'
    :param interval: Kline interval, e.g. '1h'
    :param limit: Number of candlesticks to retrieve
    :return: List of candlestick data
    """
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    return data


if __name__ == '__main__':
    # Define parameters for the query
    symbol = 'ETHUSDT'
    interval = '1h'  # 1-hour intervals
    limit = 24     # Last 24 hours

    try:
        candlestick_data = fetch_candlestick_data(symbol, interval, limit)
        formatted_data = []
        for candle in candlestick_data:
            # Each candle format:
            # [ open time, open, high, low, close, volume, close time, ... ]
            open_time_ms = candle[0]  # in milliseconds
            close_price = float(candle[4])
            # Convert timestamp to human-readable format
            time_str = datetime.fromtimestamp(open_time_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
            formatted_data.append({
                'token_name': symbol,
                'token_price': close_price,
                'time': time_str
            })
        
        # Convert the formatted data into a JSON formatted string
        json_output = json.dumps(formatted_data, indent=4, ensure_ascii=False)
        print(json_output)
    except Exception as e:
        print('Error fetching data:', e) 