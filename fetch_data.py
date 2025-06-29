import ccxt
import pandas as pd
import time
from datetime import datetime

# kraken = ccxt.kraken({
#     'apiKey': 'YOUR_PUBLIC_API_KEY',
#     'secret': 'YOUR_SECRET_PRIVATE_KEY',
# })

def fetch_data(symbol, timeframe, since):
    """
    Fetches historical OHLCV data and saves it to a CSV file.
    """
    binance = ccxt.binance()
    limit = 1000 # Max candles per request for Binance
    all_data = []

    since_datetime = datetime.strptime(since, "%Y-%m-%d")
    since_timestamp = int(since_datetime.timestamp() * 1000)

    while True:
        try:
            # Fetch ohlcv data from Binance

            ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=limit)

            # Check if the API returned any data
            if len(ohlcv):
                all_data.extend(ohlcv)

                # Update the 'since' timestamp for the next iteration                
                last_candle_timestamp = ohlcv[-1][0] # The first element in each ohlcv entry is the timestamp
                since_timestamp = last_candle_timestamp + 1 # ...and set 'since' to that timestamp + 1 millisecond

                first_date = datetime.fromtimestamp(all_data[0][0] / 1000)
                last_date = datetime.fromtimestamp(all_data[-1][0] / 1000)

                print(f"   Fetched {len(all_data)} candles from {first_date} to {last_date}")

            else:
                # If fetch_ohlcv() returns an empty list, we've reached the most recent data
                print("\n   No more data to fetch. Reached the current time.")
                break # Exit the loop

            # Wait a moment before the next request to avoid getting banned.
            time.sleep(binance.rateLimit / 1000)

        except ccxt.NetworkError as e:
            print(f"\n   A network error occurred: {e}. Retrying in 2 seconds...")
            time.sleep(2)   # Wait before retrying

        except ccxt.ExchangeError as e:
            print(f"\n   An exchange error occurred: {e}. Stopping.")
            break # Exit on exchange errors

    print("\n   Fetching complete.")

    return all_data


def save_data_to_csv(all_data, filename):
    """
    Save the fetched data to a CSV file.
    """

    data = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Convert timestamp to datetime
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
    # Reorder columns for clarity
    data = data[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    data.to_csv(filename, index=False) # index=False prevents pandas from writing a useless row index column.
    print(f"   Trades saved to {filename}")

    return filename

if __name__ == "__main__":
    symbol = 'BTC/USDT'
    timeframes = ["1m", "15m", "1h", "4h", "1d"]
    since = "2024-01-01"  # Start fetching data from this date

    for timeframe in timeframes:
        print(f"\nFetching data for {symbol} with timeframe {timeframe} from Binance...")

        all_data = fetch_data(symbol, timeframe, since)

        filename = f"binance_BTC_USDT_ohlcv_{timeframe}.csv"
        save_data_to_csv(all_data, filename)
