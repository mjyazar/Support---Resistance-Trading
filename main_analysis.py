import pandas as pd
import logging

# Project's configuration settings
import config

# Import our custom analysis functions
from analysis.volume_analysis import calculate_volume_profile, find_significant_levels
from analysis.pivot_points import calculate_pivot_points, plot_pivot_points
from analysis.fractals import calculate_fractals


def setup_logging():
    """Configures the logging system."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.LOGS_DIR / 'project.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'), # 'a' for append
            logging.StreamHandler()
        ]
    )


def run_analysis():
    """
    Main function to load data and run multiple analysis methods using settings from the config.py file.
    """
    setup_logging()
    logging.info("--- Starting Analysis Run ---")

    symbol = config.SYMBOLS[0]  # Use the first symbol from the config
    
    # --- Analysis 1: Volume Profile Analysis ---
    logging.info(f"--- Running Analysis 1: Volume Profile Analysis (on {config.TIMEFRAMES[2]} data) ---")
    data_file_1h = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_{config.TIMEFRAMES[2]}.csv"

    if data_file_1h.exists():
        logging.info(f"Loading (1h) data from {data_file_1h}...")
        df_1h = pd.read_csv(data_file_1h, parse_dates=['datetime'])
        
        logging.info("Calculating Volume Profile...")
        profile = calculate_volume_profile(df_1h, num_bins=config.VOLUME_BINS)
        # levels: {poc: {price_midpoint, volume}, high_volume_bins: [price_midpoints], low_volume_bins: [price_midpoints]}
        levels = find_significant_levels(profile, prominence_factor=config.VOLUME_PROMINENCE)

        logging.info(f"Volume Profile POC: ${levels['poc']['price_midpoint']:.2f}")
        logging.info(f"High Volume Nodes: {len(levels['high_volume_bins'])} levels found")
        logging.info(f"Low Volume Nodes: {len(levels['low_volume_bins'])} levels found")
    else:
        logging.warning(f"{config.TIMEFRAMES[2]} data file not found. Skipping Volume Profile.")


    # --- Analysis 2: Pivot Point Analysis ---
    logging.info(f"--- Running Analysis 2: Pivot Point Analysis (on {config.TIMEFRAMES[4]} data) ---")
    data_file_1d = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_{config.TIMEFRAMES[4]}.csv"
    file_name_1d = data_file_1d.name

    if data_file_1d.exists():
        logging.info(f"Loading (1d) data from {data_file_1d}...")
        df_1d = pd.read_csv(data_file_1d, parse_dates=['datetime'])

        logging.info("Calculating Daily Pivot Points...")
        pivots_df = calculate_pivot_points(df_1d.copy())

        latest_pivots = pivots_df.iloc[-1]
        logging.info("Latest Dynamic Pivot Levels (for today):")
        logging.info(f"  Latest Dynamic Pivot Levels (for today): R1=${latest_pivots['r1']:.2f}, S1=${latest_pivots['s1']:.2f}")
        # Plot the chart using the configured number of days
    else:
        logging.warning(f"{config.TIMEFRAMES[4]} data file not found. Skipping Pivot Points.")


    # --- Analysis 3: Fractal Analysis ---
    logging.info(f"--- Running Analysis 3: Fractal Analysis (on {config.TIMEFRAMES[4]} data) ---")
    if data_file_1d.exists():
        # We can reuse the daily DataFrame
        fractals_df = calculate_fractals(df_1d.copy())

        recent_highs = fractals_df.dropna(subset=['resistance']).tail(1)
        logging.info(f"Most recent fractal high found at: ${recent_highs.iloc[0]['resistance']:.2f}")


    logging.info("--- Analysis Run Finished ---")
    

if __name__ == "__main__":
    run_analysis()
