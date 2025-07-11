import pandas as pd
import numpy as np
import plotly.graph_objects as go

# https://www.investopedia.com/terms/p/pivotpoint.asp#toc-limitations-and-considerations
# https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/pivot-points-resistance-support

def calculate_pivot_points(data):
    """
    
    """

    previous_high = data['high'].shift(1)
    previous_low = data['low'].shift(1)
    previous_close = data['close'].shift(1)

    pivot_point = (previous_high + previous_low + previous_close) / 3

    data['pivot'] = pivot_point
    data['r1'] = (pivot_point * 2) - previous_low
    data['s1'] = (pivot_point * 2) - previous_high

    data['r2'] = pivot_point + (previous_high - previous_low)
    data['s2'] = pivot_point - (previous_high - previous_low)

    data['r3'] = data['r1'] + (previous_high - previous_low)
    data['s3'] = data['s1'] - (previous_high - previous_low)

    return data


def plot_pivot_points(data, filename, symbol):
    
    fig = go.Figure(data=go.Candlestick(x=data.index,
                                        open=data['open'],
                                        high=data['high'],
                                        low=data['low'],
                                        close=data['close'],
                                        name="Price"))

    pivot_levels = {'pivot': {'color': 'blue', 'dash': 'solid'},
                    'r1': {'color': 'red', 'dash': 'solid'},
                    's1': {'color': 'green', 'dash': 'solid'},
                    'r2': {'color': 'red', 'dash': 'solid'},
                    's2': {'color': 'green', 'dash': 'solid'},
                    'r3': {'color': 'red', 'dash': 'solid'},
                    's3': {'color': 'green', 'dash': 'solid'}
                    }
    
    for level, style in pivot_levels.items():
        fig.add_trace(go.Scatter(x=data.index,
                                 y=data[level],
                                 mode='lines',
                                 name=level.upper(),
                                 line=dict(color=style['color'], dash=style['dash'])
                                 ))

    fig.update_layout(title=f'<b>{symbol} Daily Price and Pivot Points</b>',
                      xaxis_title='Date',
                      yaxis_title='Price (USDT)',
                      xaxis_rangeslider_visible=False, # Hide the bulky range slider for a cleaner look
                      template='plotly_white',
                      legend_title="Levels"
                      )

    fig.show()
