import talib as ta
import pandas as pd
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules


def initialize(context):
    print('初始化策略')
    context.asset = symbol('IBM')
    context.adx_buy_line = 40
    context.adx_sell_line = 20
    context.adx_window = 7

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    # 获取过去7天的收盘价
    history = data.history(assets=context.asset,
                           fields=['close', 'high', 'low'],
                           bar_count=context.adx_window * 2,
                           frequency='1d')

    date = history.index.values[-1]
    high = history['high'].values
    low = history['low'].values
    close = history['close'].values

    adx = ta.ADX(high, low, close, timeperiod=context.adx_window)

    record(price=data.current(symbol('IBM'), 'close'),
           adx=adx[-1])

    buy_signal_triggered = False
    sell_signal_triggered = False

    if adx[-1] > context.adx_buy_line:
        buy_signal_triggered = True
    elif adx[-1] < context.adx_sell_line:
        sell_signal_triggered = True

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>买入')
        order_target_percent(context.asset, 0.5)
    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>卖出')
        order_target_percent(context.asset, 0.0)
    else:
        print(str(date) + '==>无交易')


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



