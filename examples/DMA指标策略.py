import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
DMA指标是属于趋向类指标，也是一种趋势分析指标。
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.bar_count = 60
    context.short_window = 5
    context.long_window = 20
    context.ama_window = 10
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close'],
                           bar_count=context.bar_count,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values

    sma_short = ta.SMA(close, timeperiod=context.short_window)
    sma_long = ta.SMA(close, timeperiod=context.long_window)

    dma = sma_short - sma_long
    ama = ta.SMA(dma, timeperiod=context.ama_window)

    buy_signal_triggered = False
    sell_signal_triggered = False

    price = data.current(context.asset, 'close')
    record(price=price)

    if dma[-1] > ama[-1]:
        buy_signal_triggered = True
    if dma[-1] < ama[-1]:
        sell_signal_triggered = True

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>Buy')
        order_target_percent(context.asset, 0.5)

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>Sell')
        order_target_percent(context.asset, 0.0)
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime(pd.Timestamp('2012-4-1', tz='utc'))
    end_session = pd.to_datetime(pd.Timestamp('2012-10-30', tz='utc'))
    bundle_name = "custom-csv-bundle"
    capital = 1000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
