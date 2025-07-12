import ccxt
import pandas as pd
import time
from datetime import datetime

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
            print(f"   Fetched {len(all_ohlcv)} candles from {first_date} to {last_date}")

            # Respect the API rate limit
            time.sleep(binance.rateLimit / 1000)

        except ccxt.NetworkError as e:
            print(f"\n   A network error occurred: {e}. Retrying in 2 seconds...")
            time.sleep(2)   # Wait before retrying

        except ccxt.ExchangeError as e:
            print(f"\n   An exchange error occurred: {e}. Stopping.")
            break # Exit on exchange errors

    print("\n   Fetching complete.")

    return all_ohlcv


def main():
    """
    Main function to fetch and save historical OHLCV data for all symbols and timeframes defined in the config file.
    """
    # Ensure the data directory exists, create it if it doesn't.
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Loop through all symbols and timeframes from the config file.
    for symbol in config.SYMBOLS:
        for timeframe in config.TIMEFRAMES:
            print(f"\nProcessing: {symbol} - {timeframe}")
            
            # Construct the output file path using the config directory.
            filepath = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_{timeframe}.csv"

            # Check if the data already exists to avoid re-downloading.
            if filepath.exists():
                print(f"Data already exists at '{filepath}'. Skipping.")
                continue

            # Fetch the data.
            print(f"Fetching data from {config.SINCE_DATE}...")
            ohlcv_data = fetch_historical_ohlcv(symbol, timeframe, config.SINCE_DATE)

            # Save the data if any was fetched.
            if ohlcv_data:
                # Convert list to DataFrame and save
                df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
                df.to_csv(filepath, index=False)
                print(f"Data for {symbol} - {timeframe} saved successfully.")
            else:
                print("No new data fetched.")


if __name__ == "__main__":
    main()
    print("\nData fetching complete.")
    print(f"Data files saved in: {config.DATA_DIR}")
    print("You can now run the analysis script: 'python main_analysis.py'")
