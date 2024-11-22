from flask import Flask, render_template
import asyncio
from stock_analysis import check_rsi  # Make sure this is an async function
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/rsi_indicator')
def rsi_indicator():
    stocks = [
        "crude",
        "Tesla",
    ]
    results = []

    # Create an event loop to run async functions in Flask
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Fetching RSI data for each stock
    for stock in stocks:
        rsi_data = loop.run_until_complete(check_rsi(stock))  # Run async function
        if 'close_prices' in rsi_data and 'rsi_value' in rsi_data:
            # Append the stock data if both close_prices and rsi_value are available
            closePrice =rsi_data['close_prices']
            results.append({
                "stock": stock,
                "close_price_data": list(closePrice['Close'].apply(lambda x: x)),  # List of close prices
                "rsi_value": rsi_data['rsi_value'],  # RSI value
            })
        else:
            # Append an error message if required data is missing
            results.append({
                "stock": stock,
                "error": "No valid data found for this stock."  # Error message if no data is returned
            })

    return render_template('rsi_indicator.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
