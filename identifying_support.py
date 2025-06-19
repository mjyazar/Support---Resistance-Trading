import yfinance as yf

# get historical data (hourly)
price_data = yf.download("MSTR", start="2025-04-29", end="2025-06-19", interval="5m")

total_trading_volume = price_data['Volume'].sum()
probabilities = {}

# for every price, calculate the volume weighted probability of being at that level
# if a level has a high probability, it is likely a support or resistance level
for index, row in price_data.iterrows():
    price = row['Close']
    volume = row['Volume']
    # convert to a float to ensure correct calculations
    price = float(price)
    volume = float(volume)
    probability = volume / total_trading_volume
    # add the probabilities to the dict
    if price not in probabilities:
        probabilities[price] = 0
    probabilities[price] += probability

# next steps, sort the probabilities and plot a histogram
# this is a good video on the volume profile indicator:
# https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/
