import pandas as pd
import plotly.graph_objects as go

def calculate_fractals(data):
    """"
    A bearish (up) fractal occurs at a candle if its high is the highest
    among a 5-candle sequence. A bullish (down) fractal occurs if its low
    is the lowest. This function uses a 5-period window (2 past, current, 2 future).
    """

    data['resistance'] = data['high'][(data['high'] > data['high'].shift(1)) &
                                      (data['high'] > data['high'].shift(2)) &
                                      (data['high'] > data['high'].shift(-1)) &
                                      (data['high'] > data['high'].shift(-2))]
    
    data['support'] = data['high'][(data['high'] > data['high'].shift(1)) &
                                   (data['high'] > data['high'].shift(2)) &
                                   (data['high'] > data['high'].shift(-1)) &
                                   (data['high'] > data['high'].shift(-2))]

    return data

def plot_fractals(data, filename, symbol):
    fig = go.Figure(data=go.Candlestick(x=data.index,
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'],
                                         name="Price"))
    