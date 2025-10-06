# crypto_analysis_project/main_backtest.py

import pandas as pd
import numpy as np
import logging

import config
from analysis.pivot_points import calculate_pivot_points
from backtester import run_vectorized_backtest

def setup_logging():
    """Configures the logging system."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.LOGS_DIR / 'project.log'
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )

def backtesting(ohlcv_data, confluence_zones):
    """
    Main function to run the backtest.
    """
    trades = []
    in_trade = False

    for i, candle in ohlcv_data.iterrows():
        if in_trade:
            pass


        current_price = ohlcv_data.iloc[-1]['close']

        if not in_trade:
            for zone in confluence_zones:
                zone_type = "Resistance" if zone['start_price'] > current_price else "Support"
                