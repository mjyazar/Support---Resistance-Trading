import ccxt
import pandas as pd
import time
from datetime import datetime
import logging

import config
# https://github.com/ccxt/ccxt?tab=readme-ov-file#usage
# https://docs.ccxt.com/#/

def fetch_historical_ohlcv(symbol, timeframe, since):
    """
    Fetches historical OHLCV data and saves it to a CSV file.
    """
    binance = ccxt.binance()
    limit = 1000 # Max candles per request for Binance

    # Convert the 'since' date from the config file to a timestamp
    since_datetime = datetime.strptime(since, "%Y-%m-%d")
    since_timestamp = int(since_datetime.timestamp() * 1000)

    all_ohlcv = []

    while True:
        try:
            # Fetch ohlcv data from Binance
            ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=limit)

            # Check if the API returned any data
            if not ohlcv:
                # No more data available
                break

            all_ohlcv.extend(ohlcv)

            # Update the 'since' timestamp for the next iteration                
            last_candle_timestamp = ohlcv[-1][0] # The first element in each ohlcv entry is the timestamp
            since_timestamp = last_candle_timestamp + 1 # ...and set 'since' to that timestamp + 1 millisecond

            # Progress indicator
            first_date = datetime.fromtimestamp(all_ohlcv[0][0] / 1000)
            last_date = datetime.fromtimestamp(all_ohlcv[-1][0] / 1000)
            logging.info(f"   Fetched {len(all_ohlcv)} candles for {symbol}-{timeframe}, from {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}")

            # Respect the API rate limit
            time.sleep(binance.rateLimit / 1000)

        except ccxt.NetworkError as e:
            logging.error(f"\n   A network error occurred while fetching {symbol}-{timeframe}: {e}. Retrying in 2 seconds...")
            time.sleep(2)   # Wait before retrying

        except ccxt.ExchangeError as e:
            logging.error(f"\n   An exchange error occurred while fetching {symbol}-{timeframe}: {e}. Stopping,")
            break # Exit on exchange errors

    logging.info("\n   Fetching complete.")

    return all_ohlcv


def setup_logging():
    """Configures the logging system."""
    # Ensure the logs directory exists
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure logging to write to a file and to the console
    log_file = config.LOGS_DIR / 'project.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def main():
    """
    Main function to fetch and save historical OHLCV data for all symbols and timeframes defined in the config file.
    """
    setup_logging()
    logging.info("--- Starting Data Fetching Process ---")
    
    # Ensure the data directory exists, create it if it doesn't.
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Loop through all symbols and timeframes from the config file.
    for symbol in config.SYMBOLS:
        for timeframe in config.TIMEFRAMES:
            logging.info(f"\nProcessing: {symbol} - {timeframe}")
            
            # Construct the output file path using the config directory.
            filepath = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_{timeframe}.csv"

            # Check if the data already exists to avoid re-downloading.
            if filepath.exists():
                logging.info(f"Data already exists at '{filepath}'. Skipping.")
                continue

            # Fetch the data.
            logging.info(f"Fetching data from {config.SINCE_DATE}...")
            ohlcv_data = fetch_historical_ohlcv(symbol, timeframe, config.SINCE_DATE)

            # Save the data if any was fetched.
            if ohlcv_data:
                # Convert list to DataFrame and save
                df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
                df.to_csv(filepath, index=False)
                logging.info(f"Data for {symbol} - {timeframe} saved successfully.")
            else:
                logging.warning("No new data fetched.")

    logging.info("--- Data Fetching Process Finished ---")


if __name__ == "__main__":
    main()
    print("\nData fetching complete.")
    print(f"Data files saved in: {config.DATA_DIR}")
    print("You can now run the analysis script: 'python main_analysis.py'")
