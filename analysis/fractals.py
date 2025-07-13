import pandas as pd
import plotly.graph_objects as go

def calculate_fractals(data):
    """"
    A bearish (up) fractal occurs at a candle if its high is the highest
    among a 5-candle sequence. A bullish (down) fractal occurs if its low
    is the lowest. This function uses a 5-period window (2 past, current, 2 future).
    """

    """
    Identifies bearish (up) and bullish (down) fractals in OHLC data.

    A bearish fractal marks a potential resistance level and occurs at a candle
    if its high is the highest among a 5-candle sequence.

    A bullish fractal marks a potential support level and occurs at a candle
    if its low is the lowest among a 5-candle sequence.

    Args:
        data: A DataFrame with ohlcv data.

    Returns:
        pd.DataFrame: The original DataFrame with two new columns:
                      'fractal_high' and 'fractal_low', marking the price
                      at which a fractal occurred. Other rows will be NaN.
    """

    is_fractal_high = ((data['high'] > data['high'].shift(1)) &
                       (data['high'] > data['high'].shift(2)) &
                       (data['high'] > data['high'].shift(-1)) &
                       (data['high'] > data['high'].shift(-2)))

    # --- Condition for a bullish (down) fractal (Corrected Logic) ---
    # The low of the current candle is less than the 2 previous and 2 future lows.
    is_fractal_low = ((data['low'] < data['low'].shift(1)) &
                      (data['low'] < data['low'].shift(2)) &
                      (data['low'] < data['low'].shift(-1)) &
                      (data['low'] < data['low'].shift(-2)))

    # Assign the high or low price to the new columns where the condition is True.
    # Non-fractal rows will automatically be filled with NaN (Not a Number).
    data['fractal_high'] = data['high'][is_fractal_high]
    data['fractal_low'] = data['low'][is_fractal_low]

    return data
