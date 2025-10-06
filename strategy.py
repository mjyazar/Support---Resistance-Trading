"""
Trading Strategy: Support & Resistance Confluence Zones

This module defines the trading rules and generates signals based on 
confluence zones and price action.
"""

import pandas as pd
import numpy as np
import logging


def generate_signals(df, confluence_zones, buffer_pct=0.2):
    """
    Generates trading signals based on confluence zones.
    
    Strategy Logic:
    - LONG: Price touches a support zone from above
    - SHORT: Price touches a resistance zone from below
    - EXIT: Price moves significantly away from zone or hits opposite zone
    
    Args:
        df: DataFrame with OHLCV data
        confluence_zones: List of dicts with 'start_price', 'end_price', 'sources'
        buffer_pct: Additional percentage buffer around zones (default 0.2%)
    
    Returns:
        DataFrame with added 'signal' column (1=long, -1=short, 0=flat)
    """
    df = df.copy()
    df['signal'] = 0
    
    if not confluence_zones:
        logging.warning("No confluence zones provided. All signals will be 0.")
        return df
    
    # Get current price to classify zones
    current_price = df['close'].iloc[-1]
    
    # Separate zones into support and resistance
    support_zones = []
    resistance_zones = []
    
    for zone in confluence_zones:
        zone_mid = (zone['start_price'] + zone['end_price']) / 2
        if zone_mid < current_price:
            support_zones.append(zone)
        else:
            resistance_zones.append(zone)
    
    logging.info(f"Identified {len(support_zones)} support zones and {len(resistance_zones)} resistance zones")
    
    # Generate signals for each candle
    for i in range(1, len(df)):
        current_close = df['close'].iloc[i]
        current_low = df['low'].iloc[i]
        current_high = df['high'].iloc[i]
        prev_close = df['close'].iloc[i-1]
        
        # Check if price is touching any support zone (potential LONG)
        for zone in support_zones:
            zone_bottom = zone['start_price'] * (1 - buffer_pct/100)
            zone_top = zone['end_price'] * (1 + buffer_pct/100)
            
            # Price touched or entered zone from above
            if (current_low <= zone_top and 
                prev_close > zone_top and 
                current_close > zone_bottom):
                
                # Count number of confluence sources for zone strength
                zone_strength = len(zone['sources'])
                
                # Only take signal if zone has at least 2 sources
                if zone_strength >= 2:
                    df.loc[df.index[i], 'signal'] = 1
                    logging.debug(f"LONG signal at {df['datetime'].iloc[i]}: "
                                  f"Price {current_close:.2f} touched support zone "
                                  f"{zone['start_price']:.2f}-{zone['end_price']:.2f} "
                                  f"(strength: {zone_strength})")
                    break  # Only one signal per candle
        
        # Check if price is touching any resistance zone (potential SHORT)
        for zone in resistance_zones:
            zone_bottom = zone['start_price'] * (1 - buffer_pct/100)
            zone_top = zone['end_price'] * (1 + buffer_pct/100)
            
            # Price touched or entered zone from below
            if (current_high >= zone_bottom and 
                prev_close < zone_bottom and 
                current_close < zone_top):
                
                zone_strength = len(zone['sources'])
                
                if zone_strength >= 2:
                    df.loc[df.index[i], 'signal'] = -1
                    logging.debug(f"SHORT signal at {df['datetime'].iloc[i]}: "
                                f"Price {current_close:.2f} touched resistance zone "
                                f"{zone['start_price']:.2f}-{zone['end_price']:.2f} "
                                f"(strength: {zone_strength})")
                    break
    
    # Add signal statistics
    long_signals = (df['signal'] == 1).sum()
    short_signals = (df['signal'] == -1).sum()
    logging.info(f"Generated {long_signals} LONG signals and {short_signals} SHORT signals")
    
    return df


def generate_signals_with_confirmation(df, confluence_zones, buffer_pct=0.2, 
                                      use_volume=True, use_momentum=False):
    """
    Enhanced signal generation with additional confirmation filters.
    
    Additional Filters:
    - Volume confirmation: Higher volume on touch
    - Momentum filter: RSI or price momentum confirmation
    
    Args:
        df: DataFrame with OHLCV data
        confluence_zones: List of confluence zone dictionaries
        buffer_pct: Zone buffer percentage
        use_volume: Require above-average volume for signals
        use_momentum: Add momentum confirmation (requires RSI calculation)
    
    Returns:
        DataFrame with 'signal' column
    """
    # Start with basic signal generation
    df = generate_signals(df, confluence_zones, buffer_pct)
    
    if use_volume:
        # Calculate average volume (20-period)
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        # Filter signals: keep only if volume > average
        volume_filter = df['volume'] > df['volume_ma']
        df.loc[~volume_filter, 'signal'] = 0
        
        logging.info("Applied volume confirmation filter")
    
    if use_momentum:
        # Simple RSI calculation (14-period)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # For LONG signals, prefer RSI < 50 (oversold)
        # For SHORT signals, prefer RSI > 50 (overbought)
        long_momentum_filter = (df['signal'] == 1) & (df['rsi'] < 50)
        short_momentum_filter = (df['signal'] == -1) & (df['rsi'] > 50)
        
        # Reset signals that don't meet momentum criteria
        df.loc[(df['signal'] == 1) & ~long_momentum_filter, 'signal'] = 0
        df.loc[(df['signal'] == -1) & ~short_momentum_filter, 'signal'] = 0
        
        logging.info("Applied momentum (RSI) confirmation filter")
    
    return df


def add_stop_loss_take_profit(df, confluence_zones, sl_pct=2.0, tp_pct=4.0):
    """
    Adds stop loss and take profit levels based on confluence zones.
    
    This is for more advanced backtesting implementations that track
    individual trades rather than just position signals.
    
    Args:
        df: DataFrame with signals
        confluence_zones: Zone information
        sl_pct: Stop loss percentage from entry
        tp_pct: Take profit percentage from entry
    
    Returns:
        DataFrame with 'stop_loss' and 'take_profit' columns
    """
    df = df.copy()
    df['stop_loss'] = np.nan
    df['take_profit'] = np.nan
    
    for i in range(len(df)):
        if df['signal'].iloc[i] == 1:  # Long
            entry_price = df['close'].iloc[i]
            df.loc[df.index[i], 'stop_loss'] = entry_price * (1 - sl_pct/100)
            df.loc[df.index[i], 'take_profit'] = entry_price * (1 + tp_pct/100)
            
        elif df['signal'].iloc[i] == -1:  # Short
            entry_price = df['close'].iloc[i]
            df.loc[df.index[i], 'stop_loss'] = entry_price * (1 + sl_pct/100)
            df.loc[df.index[i], 'take_profit'] = entry_price * (1 - tp_pct/100)
    
    return df


# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    sample_df = pd.DataFrame({
        'datetime': pd.date_range('2024-01-01', periods=100, freq='1H'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    sample_zones = [
        {'start_price': 95, 'end_price': 97, 'sources': ['POC', 'HVN', 'Fractal Low']},
        {'start_price': 103, 'end_price': 105, 'sources': ['HVN', 'Fractal High']}
    ]
    
    result = generate_signals(sample_df, sample_zones)
    print(f"\nGenerated {(result['signal'] != 0).sum()} total signals")
    print(f"Signal distribution:\n{result['signal'].value_counts()}")