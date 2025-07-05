import pandas as pd
from pathlib import Path

# from analysis.volume_probability import calculate_volume_profile
from analysis.volume_profile import calculate_volume_profile, find_peak_volume_bins


def run_analysis():
    data_folder = Path("data")
    """
    data_files = list(data_folder.glob("*.csv"))
    
    
    for file in data_files:
        if not file.exists():
            print(f"Error: Data file not found at {file}")
            print("Please run fetch_data.py first.")
            return
    
        data = pd.read_csv(file, parse_dates=["datetime"], set_index="datetime")

        calculate_volume_profile(data)
    """

    file = data_folder / "binance_BTC_USDT_ohlcv_1m.csv"
    data = pd.read_csv(file, parse_dates=["datetime"], index_col="datetime")
    calculate_volume_profile(data)
    find_peak_volume_bins(calculate_volume_profile(data))

if __name__ == "__main__":
    run_analysis()
