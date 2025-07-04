import pandas as pd
import numpy as np

def calculate_volume_profile(data, number_bins=100):

    min_price = data['low'].min()
    max_price = data['high'].max()

    price_bins = np.linspace(min_price, max_price, number_bins)

    volume_bins = np.zeros(number_bins - 1)

    for bin in range(number_bins - 1):
        