from pathlib import Path

# --- PROJECT STRUCTURE ---
# Defines the base directory of the project.
BASE_DIR = Path(__file__).resolve().parent
# Defines the directory where data files are stored.
DATA_DIR = BASE_DIR / "data"
# Defines the directory where log files are stored.
LOGS_DIR = BASE_DIR / "logs"


# --- DATA FETCHING ---
# The list of cryptocurrency symbols to analyze.
SYMBOLS = ["BTC/USDT"]
# The timeframes to download data for.
TIMEFRAMES = ["1m", "15m", "1h", "4h", "1d"]
# The start date for fetching historical data.
SINCE_DATE = "2024-01-01"


# --- ANALYSIS PARAMETERS ---
# Parameters for Volume Analysis
VOLUME_BINS = 200 # Number of price bins for the volume profile.
VOLUME_PROMINENCE = 2.0 # How much larger a peak must be to be a "High Volume Node".


# Parameters for Fractal Analysis
# (Currently none, but we can add lookback periods etc. later)


# --- VISUALIZATION PARAMETERS ---
# Number of recent days to display on charts.
CHART_DAYS = 1000
