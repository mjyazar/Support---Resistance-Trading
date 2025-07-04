import pandas as pd
import numpy as np
import plotly.graph_objects as go

def load_data(filepath):
    """f
    Loads OHLCV data from a specified CSV file path.
    """

    print(f"Loading data from {filepath}...")
    try:
        # Load the CSV, treat the "datetime" column as dates
        data = pd.read_csv(filepath, parse_dates=['datetime'])
        print("Data loaded successfully.")
        return data
    
    except FileNotFoundError:
        # Error if the fetch script hasn't been run yet
        print(f"Error: File not found at {filepath}")
        print("Run the fetch_data.py script first to generate the data file.")
        return None

def plot_graph(data):

    fig = go.Figure(data=go.Ohlc(x=data['datetime'],
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close']))
    fig.update_layout(title='OHLC Chart', 
                      xaxis_title='Date',
                      yaxis_title='Price')


    fig.show()

if __name__ == "__main__":
    symbol = 'BTC/USDT'
    timeframe = '1h'

    filepath = f"data/binance_{symbol.replace('/', '_')}_ohlcv_{timeframe}.csv"

    # Load the data
    ohlc_data = load_data(filepath)

    print(ohlc_data)

    plot_graph(ohlc_data)
