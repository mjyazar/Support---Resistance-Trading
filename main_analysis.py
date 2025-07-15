import pandas as pd
import logging

# Project's configuration settings
import config

# Import our custom analysis functions
from analysis.volume_analysis import calculate_volume_profile, find_significant_levels
from analysis.pivot_points import calculate_pivot_points
from analysis.fractals import calculate_fractals
from analysis.oscillators import add_rsi


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


def find_confluence_zones(levels, tolerance_percent=0.5):
    """
    Finds clusters of S/R levels that are close to each other.

    Args:
        levels (list of dicts): A list where each dict has 'price' and 'source'.
        tolerance_percent (float): The percentage range to consider levels as being in the same cluster.

    Returns:
        list of dicts: A list of confluence zones, each with a start/end price and sources.
    """

    if not levels:
        return []

    sorted_levels = sorted(levels, key=lambda x: x['price'])

    clusters = [] # Becomes a list of list of dictionaries
    current_cluster = [sorted_levels[0]] # A list

    for i in range(1, len(sorted_levels)):
        current_price = sorted_levels[i]['price']
        cluster_base_price = current_cluster[0]['price']
        
        # Check if the current level is within the tolerance of the cluster's starting price
        if (current_price - cluster_base_price) / cluster_base_price * 100 <= tolerance_percent:
            current_cluster.append(sorted_levels[i])

        else:
            # The current level is too far away, so the previous cluster is complete
            clusters.append(current_cluster)
            # Start a new cluster with the current level
            current_cluster = [sorted_levels[i]]

    # Add the last cluster
    clusters.append(current_cluster)

    # Filter for actual confluence zones (more than one level in a cluster)
    confluence_zones = []
    for cluster in clusters:
        if len(cluster) > 1:
            zone = {'start_price': cluster[0]['price'],
                    'end_price': cluster[-1]['price'],
                    'sources': [level['source'] for level in cluster]} # Level is a dict
            
            confluence_zones.append(zone)
            
    return confluence_zones


def run_analysis():
    """
    Main function to load data and run multiple analysis methods using settings from the config.py file.
    """
    setup_logging()
    logging.info("--- Starting Analysis Run ---")

    symbol = config.SYMBOLS[0]  # Use the first symbol from the config
    master_levels = []
    
    # Load Data
    data_file_1h = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_1h.csv"
    data_file_1d = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_1d.csv"

    if not data_file_1h.exists() or not data_file_1d.exists():
        logging.error("Required data files not found. Please run fetch_data.py.")
        return

    if not data_file_1h.exists() or not data_file_1d.exists():
        logging.error("Required data files not found. Please run fetch_data.py.")
        return

    df_1h = pd.read_csv(data_file_1h, parse_dates=['datetime'])
    df_1d = pd.read_csv(data_file_1d, parse_dates=['datetime'])


    # Volume Profile Analysis
    logging.info(f"Running Volume Profile Analysis (on {config.TIMEFRAMES[2]} data)")
    profile = calculate_volume_profile(df_1h, num_bins=config.VOLUME_BINS)
    volume_levels = find_significant_levels(profile, prominence_factor=config.VOLUME_PROMINENCE)

    logging.info(f"Volume Profile POC: ${volume_levels['poc']['price_midpoint']:.2f}")
    logging.info(f"High Volume Nodes: {len(volume_levels['hvns'])} levels found")
    logging.info(f"Low Volume Nodes: {len(volume_levels['lvns'])} levels found")

    master_levels.append({'price': volume_levels['poc']['price_midpoint'], 'source': 'POC'})
    for hvn in volume_levels['hvns']:
        master_levels.append({'price': hvn, 'source': 'HVN'})


    # Pivot Point Analysis
    logging.info(f"Running Pivot Point Analysis (on {config.TIMEFRAMES[4]} data)")
    pivots_df = calculate_pivot_points(df_1d.copy())
    latest_pivots = pivots_df.iloc[-1]

    logging.info(f"Latest Dynamic Pivot Levels (for today): R1=${latest_pivots['r1']:.2f}, S1=${latest_pivots['s1']:.2f}")

    for level_name in ['r3', 'r2', 'r1', 'pivot', 's1', 's2', 's3']:
        master_levels.append({'price': latest_pivots[level_name], 'source': f"Pivot {level_name.upper()}"})


    # Fractal Analysis
    logging.info(f"Running Fractal Analysis (on {config.TIMEFRAMES[4]} data)")
    fractals_df = calculate_fractals(df_1d.copy())
    recent_highs = fractals_df.dropna(subset=['resistance']).tail(5)
    recent_lows = fractals_df.dropna(subset=['support']).tail(5)

    for index, row in recent_highs.iterrows():
        master_levels.append({'price': row['resistance'], 'source': 'Fractal High'})

    for index, row in recent_lows.iterrows():
        master_levels.append({'price': row['support'], 'source': 'Fractal Low'})


    # Find and Report Confluence Zones
    logging.info("Finding confluence zones...")
    confluence_zones = find_confluence_zones(master_levels, tolerance_percent=0.5)

    if not confluence_zones:
        logging.info("No significant confluence zones found with the current settings.")
    else:
        logging.info(f"Found {len(confluence_zones)} Confluence Zones")
        # Determine current price to classify zones as support or resistance
        current_price = df_1d.iloc[-1]['close']
        for zone in confluence_zones:
            zone_type = "Resistance" if zone['start_price'] > current_price else "Support"
            logging.info(f"  > {zone_type} Zone: ${zone['start_price']:.2f} - ${zone['end_price']:.2f}\n"
                         f"    Sources: {', '.join(zone['sources'])}")

    logging.info("Confluence Analysis Run Finished")


if __name__ == "__main__":
    run_analysis()
