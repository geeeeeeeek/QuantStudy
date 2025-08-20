import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
摆荡指标
将资金流动情况与价格行为相对比，检测市场中资金流入和流出的情况
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.adosc_window = 14
    context.fast_period = 3
    context.slow_period = 10
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['high', 'low', 'close', 'volume'],
                           bar_count=context.adosc_window * 10,
                           frequency='1d')
    date = history.index.values[-1]
    high = history['high'].values
    low = history['low'].values
    volume = history['volume'].values
    close = history['close'].values

    # 计算ADOSC指标
    adosc = ta.ADOSC(high, low, close, volume,
                     fastperiod=context.fast_period,
                     slowperiod=context.slow_period)
    print(adosc[-1])

    current_price = data[context.asset].price
    record(price=current_price)

    buy_signal_triggered = False
    sell_signal_triggered = False

    if adosc[-1] > 0:
        buy_signal_triggered = True
    elif adosc[-1] < 0:
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
