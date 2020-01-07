import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""NATR指标"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.natr_period = 10
    context.long_multi = 0.2
    context.short_multi = 0.2
    context.pre_period = 1
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close', 'high', 'low'],
                           bar_count=context.natr_period + 1,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values
    high = history['high'].values
    low = history['low'].values

    # 使用talib计算NATR
    natr = ta.NATR(high, low, close, timeperiod=context.natr_period)[-1]

    current_price = data[context.asset].price
    record(price=current_price)

    prev_price = close[-(context.pre_period + 1)]
    # 计算上下轨
    upper = prev_price + context.long_multi * natr
    lower = prev_price - context.short_multi * natr

    buy_signal_triggered = False
    sell_signal_triggered = False

    if current_price > upper:
        buy_signal_triggered = True
    elif current_price < lower:
        sell_signal_triggered = True

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>Buy')
        order_target_percent(context.asset, 1.0)

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>Sell')
        order_target_percent(context.asset, 0.0)
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime('2012-05-01', utc=True)
    end_session = pd.to_datetime('2013-05-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
