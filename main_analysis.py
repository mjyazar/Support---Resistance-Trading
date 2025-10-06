import pandas as pd
import logging

# Project's configuration settings
import config

# Import custom analysis functions
from analysis.volume_analysis import calculate_volume_profile, find_significant_levels
from analysis.pivot_points import calculate_pivot_points
from analysis.fractals import calculate_fractals
from backtester import run_vectorized_backtest
from strategy import generate_signals, generate_signals_with_confirmation


def setup_logging():
    """Configures the logging system."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.LOGS_DIR / 'project.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[logging.FileHandler(log_file, mode='a'),
                  logging.StreamHandler()])


def run_analysis():
    """
    Main function to load data and run multiple analysis methods using settings from the config.py file.
    """
    setup_logging()
    logging.info("=" * 60)
    logging.info("--- Starting Analysis Run ---")
    logging.info("=" * 60)

    symbol = config.SYMBOLS[0]
    master_levels = {}

    # Load Data
    data_file_1h = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_1h.csv"
    data_file_1d = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_1d.csv"

    if not data_file_1h.exists() or not data_file_1d.exists():
        logging.error("Required data files not found. Please run fetch_data.py.")
        return None, None

    df_1h = pd.read_csv(data_file_1h, parse_dates=['datetime'])
    df_1d = pd.read_csv(data_file_1d, parse_dates=['datetime'])

    cutoff = pd.Timestamp(config.UNTIL)

    # Split data: Analysis (training) and Backtesting (testing)
    df_1h_analysis = df_1h[df_1h['datetime'] < cutoff].copy()
    df_1h_backtesting = df_1h[df_1h['datetime'] >= cutoff].copy()

    df_1d_analysis = df_1d[df_1d['datetime'] < cutoff].copy()
    df_1d_backtesting = df_1d[df_1d['datetime'] >= cutoff].copy()

    logging.info(f"Analysis period: {df_1h_analysis['datetime'].min()} to {df_1h_analysis['datetime'].max()}")
    logging.info(f"Backtesting period: {df_1h_backtesting['datetime'].min()} to {df_1h_backtesting['datetime'].max()}")
    logging.info(f"Analysis candles: {len(df_1h_analysis)} | Backtest candles: {len(df_1h_backtesting)}")

    # === ANALYSIS PHASE ===
    logging.info("\n" + "=" * 60)
    logging.info("PHASE 1: TECHNICAL ANALYSIS")
    logging.info("=" * 60)

    # Volume Profile Analysis
    logging.info(f"\n[1/3] Running Volume Profile Analysis on {config.TIMEFRAMES[2]} data...")
    volume_profile = calculate_volume_profile(df_1h_analysis, num_bins=config.VOLUME_BINS)
    volume_levels = find_significant_levels(volume_profile, prominence_factor=config.VOLUME_PROMINENCE)
    logging.info(f"  ✓ Volume Profile POC: ${volume_levels['poc']['price_midpoint']:.2f}")
    logging.info(f"  ✓ High Volume Nodes: {len(volume_levels['hvns'])} levels found")
    logging.info(f"  ✓ Low Volume Nodes: {len(volume_levels['lvns'])} levels found")
    master_levels['poc'] = volume_levels['poc']['price_midpoint']
    master_levels['hvns'] = volume_levels['hvns']

    # Pivot Point Analysis (UNCOMMENTED)
    logging.info(f"\n[2/3] Running Pivot Point Analysis on {config.TIMEFRAMES[4]} data...")
    pivots_df = calculate_pivot_points(df_1d_analysis)
    latest_pivots = pivots_df.iloc[-1]
    logging.info(f"  ✓ Latest Pivot Levels: R1=${latest_pivots['r1']:.2f}, S1=${latest_pivots['s1']:.2f}")
    master_levels['pivots'] = pivots_df

    # Fractal Analysis
    logging.info(f"\n[3/3] Running Fractal Analysis on {config.TIMEFRAMES[4]} data...")
    fractals_df = calculate_fractals(df_1d_analysis.copy())
    fractal_highs = fractals_df['fractal_high'].dropna()
    fractal_lows = fractals_df['fractal_low'].dropna()
    logging.info(f"  ✓ Fractal Highs: {len(fractal_highs)} identified")
    logging.info(f"  ✓ Fractal Lows: {len(fractal_lows)} identified")
    master_levels['fractals'] = fractals_df

    # === CONFLUENCE DETECTION ===
    logging.info("\n" + "=" * 60)
    logging.info("PHASE 2: CONFLUENCE ZONE DETECTION")
    logging.info("=" * 60)

    # Create flat list from master_levels for confluence function
    temp_level_list = []
    temp_level_list.append({'price': master_levels['poc'], 'source': 'POC'})
    
    for hvn in master_levels['hvns']:
        temp_level_list.append({'price': hvn, 'source': 'HVN'})

    latest_pivots = master_levels['pivots'].iloc[-1]
    for level_name in ['r3', 'r2', 'r1', 'pivot', 's1', 's2', 's3']:
        temp_level_list.append({'price': latest_pivots[level_name], 'source': f"Pivot {level_name.upper()}"})

    for index, row in master_levels['fractals'].dropna(subset=['fractal_high']).iterrows():
        temp_level_list.append({'price': row['fractal_high'], 'source': 'Fractal High'})

    for index, row in master_levels['fractals'].dropna(subset=['fractal_low']).iterrows():
        temp_level_list.append({'price': row['fractal_low'], 'source': 'Fractal Low'})

    logging.info(f"Total individual levels collected: {len(temp_level_list)}")

    # Find Confluence Zones
    confluence_zones = find_confluence_zones(temp_level_list, tolerance_percent=0.5)

    if not confluence_zones:
        logging.warning("⚠ No significant confluence zones found with current settings.")
        logging.info("Consider adjusting tolerance_percent or adding more indicators.")
        return df_1h_backtesting, []
    else:
        logging.info(f"\n✓ Found {len(confluence_zones)} Confluence Zones:")
        current_price = df_1h_analysis.iloc[-1]['close']
        
        for idx, zone in enumerate(confluence_zones, 1):
            zone_type = "RESISTANCE" if zone['start_price'] > current_price else "SUPPORT"
            zone_strength = len(zone['sources'])
            logging.info(f"\n  Zone {idx} [{zone_type}]:")
            logging.info(f"    Price Range: ${zone['start_price']:.2f} - ${zone['end_price']:.2f}")
            logging.info(f"    Strength: {zone_strength} sources")
            logging.info(f"    Sources: {', '.join(zone['sources'])}")

    # === SIGNAL GENERATION ===
    logging.info("\n" + "=" * 60)
    logging.info("PHASE 3: SIGNAL GENERATION")
    logging.info("=" * 60)

    # Generate signals on BACKTESTING data using confluence zones from ANALYSIS data
    df_with_signals = generate_signals(df_1h_backtesting, confluence_zones, buffer_pct=0.2)
    
    signal_count = (df_with_signals['signal'] != 0).sum()
    logging.info(f"✓ Generated {signal_count} trading signals")

    # === BACKTESTING ===
    logging.info("\n" + "=" * 60)
    logging.info("PHASE 4: BACKTESTING")
    logging.info("=" * 60)

    if signal_count == 0:
        logging.warning("⚠ No signals generated. Cannot run backtest.")
        logging.info("Suggestions:")
        logging.info("  - Increase tolerance_percent in confluence detection")
        logging.info("  - Adjust buffer_pct in signal generation")
        logging.info("  - Check if zones exist in the backtesting period price range")
        return df_with_signals, confluence_zones

    results = run_vectorized_backtest(df_with_signals, signal_col='signal', initial_capital=10000)
    
    logging.info("\n" + "=" * 60)
    logging.info("BACKTEST RESULTS")
    logging.info("=" * 60)
    for metric, value in results.items():
        logging.info(f"  {metric:.<30} {value}")
    logging.info("=" * 60)

    return df_with_signals, confluence_zones


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

    clusters = []
    current_cluster = [sorted_levels[0]]

    for i in range(1, len(sorted_levels)):
        current_price = sorted_levels[i]['price']
        cluster_base_price = current_cluster[0]['price']
        
        # Check if the current level is within the tolerance of the cluster's starting price
        if abs((current_price - cluster_base_price)) / cluster_base_price * 100 <= tolerance_percent:
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
            zone = {
                'start_price': cluster[0]['price'],
                'end_price': cluster[-1]['price'],
                'sources': [level['source'] for level in cluster]
            }
            confluence_zones.append(zone)
    
    return confluence_zones


if __name__ == "__main__":
    df_results, zones = run_analysis()
    
    if df_results is not None and not df_results.empty:
        logging.info("\n✓ Analysis complete!")
        logging.info(f"Results saved in memory. {len(df_results)} candles processed.")
    else:
        logging.error("\n✗ Analysis failed or returned no data.")
