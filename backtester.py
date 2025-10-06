import talib
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover


import config
from main_analysis import run_analysis

df_1h_backtesting, confluence_zones = run_analysis()
print(confluence_zones)

symbol = "ETH/USDT"  # Use the first symbol from the config
data_file_1h = config.DATA_DIR / f"binance_{symbol.replace('/', '_')}_ohlcv_1h.csv"
df_1h = pd.read_csv(data_file_1h, parse_dates=['datetime'])
df_1h.set_index("datetime", inplace=True)
df_1h.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
print(df_1h)


class RsiOscillator(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14
    
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_window)

    def next(self):
        
        # if first series is bigger than second series, sell
        # i.e. rsi is above upper bound, sell
        if crossover(self.rsi, self.upper_bound):
            self.position.close()

        # if lower bound is above rsi, buy
        elif crossover(self.lower_bound, self.rsi):
            self.buy()


bt = Backtest(GOOG, RsiOscillator, cash=100000, commission=.002, exclusive_orders=True, finalize_trades=True)

stats = bt.run()
bt.plot()
print(stats)

returns = stats["Return [%]"]

rsi_window = [i for i in range(1, 25)]


stats = bt.optimize(upper_bound=range(50, 85, 5),
                    lower_bound=range(10, 45, 5),
                    rsi_window=range(10, 30, 2),
                    maximize='Return [%]',
                    constraint=lambda param: param.upper_bound - param.lower_bound >= 20,
                    return_heatmap=True)

bt.plot(results=stats, )

print(stats)
