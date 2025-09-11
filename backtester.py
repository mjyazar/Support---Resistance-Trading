# crypto_analysis_project/backtester.py

import pandas as pd
import numpy as np

def run_vectorized_backtest(df, signal_col='signal', initial_capital=10000):
    """
    Runs a fast, vectorized backtest on a given DataFrame.

    Args:
        df (pd.DataFrame): Must contain 'close' prices and a signal column.
        signal_col (str): The name of the column containing the trading signal (1 for long, -1 for short, 0 for flat).
        initial_capital (float): The starting capital.

    Returns:
        pd.Series: A series containing key performance metrics.
    """

    # 1. Determine positions based on the signal
    # We shift the signal by 1 to ensure we trade on the NEXT candle's open, avoiding lookahead bias.
    # A signal generated at the close of day T is used to take a position for day T+1.
    positions = df[signal_col].shift(1).fillna(0)

    # 2. Calculate daily returns of the asset
    daily_returns = df['close'].pct_change()

    # 3. Calculate strategy returns
    # The return is the position taken (-1, 0, or 1) multiplied by that day's return.
    strategy_returns = positions * daily_returns

    # 4. Calculate the cumulative equity curve
    cumulative_returns = (1 + strategy_returns).cumprod()
    equity_curve = initial_capital * cumulative_returns

    # --- Performance Metrics ---
    total_return = (equity_curve.iloc[-1] / initial_capital) - 1
    annualized_return = (1 + total_return) ** (365 / len(df)) - 1
    
    annualized_volatility = strategy_returns.std() * np.sqrt(365)
    
    # Assume risk-free rate is 0 for simplicity
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0
    
    # Max Drawdown
    previous_peaks = equity_curve.cummax()
    drawdown = (equity_curve - previous_peaks) / previous_peaks
    max_drawdown = drawdown.min()

    report = {
        "Total Return": f"{total_return:.2%}",
        "Annualized Return": f"{annualized_return:.2%}",
        "Annualized Volatility": f"{annualized_volatility:.2%}",
        "Max Drawdown": f"{max_drawdown:.2%}",
        "Sharpe Ratio": f"{sharpe_ratio:.2f}",
        "Final Equity": f"${equity_curve.iloc[-1]:,.2f}"
    }

    return pd.Series(report)