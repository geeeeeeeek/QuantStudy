import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
集散量（Accumulation Distribution Line 简称ADV）指标
用于估定一段时间内该证券累积的资金流量。
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.ad_window = 6
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['high', 'low', 'close', 'volume'],
                           bar_count=context.ad_window+1,
                           frequency='1d')
    date = history.index.values[-1]
    high = history['high'].values
    low = history['low'].values
    close = history['close'].values
    volume = history['volume'].values

    # 计算AD指标
    ad = ta.AD(high, low, close, volume)

    current_price = data[context.asset].price
    record(price=current_price)

    buy_signal_triggered = False
    sell_signal_triggered = False

    if ad[-1] > 0:
        buy_signal_triggered = True
    elif ad[-1] < 0:
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
    start_session = pd.to_datetime('2013-01-01', utc=True)
    end_session = pd.to_datetime('2014-05-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
