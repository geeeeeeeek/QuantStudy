import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
KDJ指标叫随机指标
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    # 快线回看周期为9
    context.fastk_period = 9
    # 慢线回看周期为3
    context.slowk_period = 3
    context.slowd_period = 3
    # 使用简单平均
    context.slowk_matype = 0
    # 历史窗口
    context.kdj_window = 100
    # 超买信号线
    context.over_buy_signal = 80
    # 超卖信号线
    context.over_sell_signal = 20

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['high', 'low', 'close'],
                           bar_count=context.kdj_window,
                           frequency='1d')
    date = history.index.values[-1]

    high = history['high'].values
    low = history['low'].values
    close = history['close'].values

    # 用talib计算K，D两条线
    K, D = ta.STOCH(high, low, close,
                    fastk_period=context.fastk_period,
                    slowk_matype=context.slowk_matype,
                    slowk_period=context.slowk_period,
                    slowd_period=context.slowd_period)
    current_k_value = K[-1]
    current_d_value = D[-1]
    previous_k_value = K[-2]
    previous_d_value = D[-2]

    buy_signal_triggered = False
    sell_signal_triggered = False

    price = data.current(context.asset, 'close')
    record(price=price)

    # 当D < 超卖线, K线和D线同时上升，且K线从下向上穿过D线时，买入
    if context.over_sell_signal > current_d_value > previous_d_value and current_k_value > previous_k_value and previous_k_value < previous_d_value and current_k_value > current_d_value:
        buy_signal_triggered = True
    # 当D > 超买线, K线和D线同时下降，且K线从上向下穿过D线时，卖出
    elif context.over_buy_signal < current_d_value < previous_d_value and current_k_value < previous_k_value and previous_k_value > previous_d_value and current_k_value < current_d_value:
        sell_signal_triggered = True

    print(current_d_value)

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print('%s ====> Buy' % date)
        order_target_percent(context.asset, 0.5)

    elif sell_signal_triggered and current_position > 0:
        print('%s ====> Sell' % date)
        order_target_percent(context.asset, 0.0)
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime('2013-05-01', utc=True)
    end_session = pd.to_datetime('2014-05-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
