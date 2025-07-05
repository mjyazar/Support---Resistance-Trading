import pandas as pd
import numpy as np

def calculate_volume_profile(data, number_bins=100):

    min_price = data['low'].min()
    max_price = data['high'].max()
    print("Minimum price:", min_price)
    print("Maximum price:", max_price)

    # Create price points for the bins
    price_points = np.linspace(min_price, max_price, number_bins + 1)

    # Volume bins needs to be 1 less than the number of points (i.e. blocks vs edges)
    volume_bins = np.zeros(number_bins)

    for bin in range(number_bins):
        # Relevant candles are those with low below the top bin, and high above bottom bin
        relevant_candles = data[(data["low"] < price_points[bin + 1]) & (data["high"] > price_points[bin])]

        # For each relevant candle, calculate how much the candle overlaps with the bin
        # To determine the proportion of volume to assign to the bin
        overlap_min = np.maximum(relevant_candles["low"], price_points[bin])
        overlap_max = np.minimum(relevant_candles["high"], price_points[bin + 1])

        overlap_range = overlap_max - overlap_min
        candle_range = relevant_candles["high"] - relevant_candles["low"]

        # Avoid division by zero for flat candles (high == low)
        candle_range[candle_range == 0] = 1

        # Assign the volume to the bin based on the overlap proportion
        volume_bins[bin] = np.sum(relevant_candles["volume"] * (overlap_range / candle_range))

    price_midpoint = (price_points[:-1] + price_points[bin + 1]) / 2

    volume_profile = pd.DataFrame({"price_midpoint": price_midpoint, 
                            "volume": volume_bins})
    
    return volume_profile


def find_peak_volume_bins(volume_profile, prominence_factor = 1.5):
    poc_index = volume_profile["volume"].idxmax()
    poc = volume_profile.loc[poc_index].to_dict()

    average_volume = volume_profile["volume"].mean()
    high_volume_bins = volume_profile[volume_profile["volume"] > (average_volume * prominence_factor)]
    low_volume_bins = volume_profile[volume_profile["volume"] < (average_volume / prominence_factor)]
    
    nodes = {"poc": poc,
             "high_volume_bins": high_volume_bins.to_list(),
             "low_volume_bins": low_volume_bins.to_list()}

    return nodes


def pivot_points(volume_profile, prominence_factor=1.5):
    print()