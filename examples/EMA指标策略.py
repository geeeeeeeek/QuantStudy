import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""EMA指标策略"""


def initialize(context):
    print("init")
    context.asset = symbol('AAPL')
    context.ema_fast_window = 5
    context.ema_slow_window = 20
    context.stop_loss_line = 5
    context.stop_win_line = 5
    # 记录净值的最大值，用于计算持仓的止损回撤
    context.max_up_to_now = None
    # 记录净值的最大值，用于计算持仓的止盈回撤
    context.min_up_to_now = None

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    buy_signal_triggered = False
    sell_signal_triggered = False
    stop_loss_signal_triggered = False
    stop_win_signal_triggered = False

    current_position = context.portfolio.positions[context.asset].amount
    print("持仓数=%d" % current_position)
    current_price = data[context.asset].price
    record(price=current_price)

    # 更新最大值
    if context.max_up_to_now is None:
        context.max_up_to_now = current_price
    elif context.max_up_to_now < current_price:
        context.max_up_to_now = current_price
    # 计算止损回撤
    current_loss_draw_down = (1 - current_price / context.max_up_to_now) * 100
    print("当前止损回撤为 %.2f%%, 止损线为 %.2f%%" % (current_loss_draw_down, context.stop_loss_line))
    if current_loss_draw_down > context.stop_loss_line:
        print("已经触发止损线信号")
        stop_loss_signal_triggered = True

    # 更新最小值
    if context.min_up_to_now is None:
        context.min_up_to_now = current_price
    elif context.min_up_to_now > current_price:
        context.min_up_to_now = current_price
    # 计算止盈回撤
    current_win_draw_down = (1 - context.min_up_to_now / current_price) * 100
    print("当前止盈回撤为 %.2f%%, 止盈线为 %.2f%%" % (current_win_draw_down, context.stop_win_line))
    if current_win_draw_down > context.stop_win_line:
        print("已经触发止盈线信号")
        stop_win_signal_triggered = True

    history = data.history(assets=context.asset,
                           fields=['open', 'high', 'low', 'close'],
                           bar_count=context.ema_slow_window + 1,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values

    # 计算EMA值
    ema_fast = ta.EMA(close, context.ema_fast_window)
    ema_slow = ta.EMA(close, context.ema_slow_window)

    # 当前快线EMA
    current_ema_fast = ema_fast[-1]
    # 当前慢线EMA
    current_ema_slow = ema_slow[-1]
    # 前一个bar的快线EMA
    pre_ema_fast = ema_fast[-2]
    # 前一个bar的慢线EMA
    pre_ema_slow = ema_slow[-2]

    # EMA快线从下向上穿过EMA慢线时，产生买入信号
    if pre_ema_fast <= pre_ema_slow and current_ema_fast > current_ema_slow:
        buy_signal_triggered = True
    # EMA快线从上向下穿过EMA慢线时，产生卖出信号
    elif pre_ema_fast >= pre_ema_slow and current_ema_fast < current_ema_slow:
        sell_signal_triggered = True

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>Buy')
        order_target_percent(context.asset, 0.5)
        context.max_up_to_now = None
        context.min_up_to_now = None

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>Sell')
        order_target_percent(context.asset, 0.0)
        context.max_up_to_now = None
        context.min_up_to_now = None
    elif stop_loss_signal_triggered and current_position > 0:
        print(str(date) + "==>Stop loss sell")
        order_target_percent(context.asset, 0.0)
        context.max_up_to_now = None
        context.min_up_to_now = None
    elif stop_win_signal_triggered and current_position > 0:
        print(str(date) + "==>Stop win sell")
        order_target_percent(context.asset, 0.0)
        context.max_up_to_now = None
        context.min_up_to_now = None
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime('2012-05-01', utc=True)
    end_session = pd.to_datetime('2013-10-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
