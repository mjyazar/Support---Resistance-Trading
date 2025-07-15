import pandas as pd
import pandas_ta as ta

def add_rsi(df, period=14):
    """
    Calculates the Relative Strength Index (RSI) using pandas-ta for 
    a fiven period and appends it as a new column named 'RSI_period'


    Args:
        df: DataFrame with a ohlcv data.
        period (int, optional): The time period for the RSI calculation. Defaults to 14.

    Returns:
        pd.DataFrame: The DataFrame with the RSI column added.
    """

    df.ta.rsi(length=period, append=True)

    return df
