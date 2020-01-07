import zipline
from zipline.api import symbol, order_target_percent, record, schedule_function
import talib as ta
import pandas as pd
from zipline.utils.events import date_rules, time_rules


def initialize(context):
    context.asset = symbol('IBM')

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(context.asset, ['close'], 40, '1d')
    date = history.index.values[-1]
    close = history['close'].values
    price = data.current(context.asset, 'close')
    record(price=price)

    macd_raw, signal, hist = ta.MACD(close, fastperiod=12,
            slowperiod=26, signalperiod=9)

    macd = macd_raw[-1] - signal[-1]

    current_position = context.portfolio.positions[context.asset].amount

    if macd > 0 and current_position == 0:
        print(str(date) + "==>触发买入")
        order_target_percent(context.asset, 1.0)
    elif macd < 0 and current_position > 0:
        print(str(date) + "==>触发卖出")
        order_target_percent(context.asset, 0.0)
    else:
        print(str(date) + "==>无交易")


if __name__ == '__main__':
    start_session = pd.to_datetime('2013-01-01', utc=True)
    end_session = pd.to_datetime('2013-10-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")

