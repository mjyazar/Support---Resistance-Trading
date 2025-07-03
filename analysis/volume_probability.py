import pandas as pd

def calculate_volume_profile(data):

    total_trading_volume = data['volume'].sum()
    probabilities = {}

    # for every price, calculate the volume weighted probability of being at that level
    # if a level has a high probability, it is likely a support or resistance level
    for index, row in data.iterrows():
        price = row['close']
        volume = row['volume'] 

        # convert to a float to ensure correct calculations
        price = float(price)
        volume = float(volume)
        probability = volume / total_trading_volume

        # add the probabilities to the dict
        if price not in probabilities:
            probabilities[price] = 0
        
        probabilities[price] += probability
    
    for price, probability in probabilities.items():
        # convert to a percentage
        probabilities[price] = round(probability * 100, 2)


    # next steps, sort the probabilities and plot a histogram
    # this is a good video on the volume profile indicator:
    # https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/

    print(probabilities)