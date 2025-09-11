import pandas as pd
import numpy as np

# https://www.investopedia.com/terms/p/pivotpoint.asp#toc-limitations-and-considerations
# https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/pivot-points-resistance-support

def calculate_pivot_points(data):
    """
    Calculates traditional daily pivot points and their support/resistance levels.

    It uses the previous day's data to calculate the current day's pivots by shifting the data by one period.

    Args:
        df: A DataFrame with 'high', 'low', 'close' columns, indexed by date.

    Returns:
        pd.DataFrame: The original DataFrame with new columns for pivot levels (pivot, r1, s1, r2, s2, r3, s3).
    """
    # Use .shift(1) to get the previous day's High, Low, and Close
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
