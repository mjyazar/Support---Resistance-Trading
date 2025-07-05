import pandas as pd
from pathlib import Path

# from analysis.volume_probability import calculate_volume_profile
from analysis.volume_profile import calculate_volume_profile, find_peak_volume_bins, pivot_points


def run_analysis():
    """
    data_folder = Path("data")
    data_files = list(data_folder.glob("*.csv"))
    
    
    for file in data_files:
        if not file.exists():
            print(f"Error: Data file not found at {file}")
            print("Please run fetch_data.py first.")
            return
    
        data = pd.read_csv(file, parse_dates=["datetime"], set_index="datetime")

        calculate_volume_profile(data)
    """
    
    data_folder = Path("data")
    file = data_folder / "binance_BTC_USDT_ohlcv_1m.csv"

    print(f"Loading data from {file}...")
    data = pd.read_csv(file, parse_dates=["datetime"], index_col="datetime")

    # Run volume profile analysis
    print("\nCalculating Volume Profile...")
    profile = calculate_volume_profile(data, bin_count=200)

    # Find the most significant levels from the profile.
    levels = find_peak_volume_bins(profile, prominence_factor=2.0)
    print(levels)


    print("\n--- Analysis Results ---")
    print(f"Point of Control (POC): Price=${levels["poc"]["price_midpoint"]:.2f}, Volume={levels["poc"]["volume"]:.2f}")
    
    print(f"\nHigh Volume Nodes ({len(levels["high_volume_bins"])} levels found):")
    print([f"${price:.2f}" for price in sorted(levels["high_volume_bins"])])
    
    print(f"\nLow Volume Nodes ({len(levels["low_volume_bins"])} levels found):")
    print([f"${price:.2f}" for price in sorted(levels["low_volume_bins"])])


    # pivot_points(calculate_volume_profile(data))

    

if __name__ == "__main__":
    run_analysis()
