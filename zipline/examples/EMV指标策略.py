import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
EMV指标
是一个常见的买卖点指标判断工具
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.emv_period = 6
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close', 'high', 'low', 'volume'],
                           bar_count=context.emv_period+2,
                           frequency='1d')
    date = history.index.values[-1]
    high = history['high']
    low = history['low']
    vol = history['volume']

    # 计算EMV
    a = (high + low) / 2
    b = a.shift(1)
    c = high - low
    em = (a - b) * c / vol
    emv = em.rolling(window=context.emv_period).sum()

    emv_current = emv[len(emv) - 1]
    emv_pre = emv[len(emv) - 2]

    print("emv_current = %f, emv_pre = %f" % (emv_current, emv_pre))

    buy_signal_triggered = False
    sell_signal_triggered = False

    price = data.current(context.asset, 'close')
    record(price=price)

    if emv_pre <= 0 < emv_current:
        buy_signal_triggered = True
    if emv_pre >= 0 > emv_current:
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
