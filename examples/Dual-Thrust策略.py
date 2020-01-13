import pandas as pd
import talib as ta
import numpy as np
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function, order_target
from zipline.utils.events import date_rules, time_rules

"""
Dual-Thrust策略
Dual Thrust是一个趋势跟踪系统
Range = Max(HH-LC, HC-LL)
上轨 = 开盘价 + K1 * range
下轨 = 开盘价 - k2 * range
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')

    # 历史窗口大小
    context.window_size = 10
    # 用户自定义的变量，可以被handle_data使用，触发空头的range.当K1<K2时，多头相对容易被触发,当K1>K2时，空头相对容易被触发
    context.K1 = 0.5
    context.K2 = 0.3
    # 止损线
    context.portfolio_stop_loss = 0.95
    # 止盈线
    context.portfolio_stop_win = 1.05
    # 是否已经触发止损
    context.stop_loss_triggered = False
    # 是否已经触发止盈
    context.stop_win_triggered = False

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    current_position = context.portfolio.positions[context.asset].amount
    print("持仓数=%d" % current_position)
    current_price = data[context.asset].price
    record(price=current_price)

    # 若已触发止盈/止损线，不会有任何操作
    if context.stop_loss_triggered:
        print("已触发止损线, 此bar不会有任何指令 ... ")
        return
    if context.stop_win_triggered:
        print("已触发止盈线, 此bar不会有任何指令 ... ")
        return

    # 检查是否到达止损线或者止盈线
    if context.portfolio.portfolio_value < context.portfolio_stop_loss * context.portfolio.starting_cash \
            or context.portfolio.portfolio_value > context.portfolio_stop_win * context.portfolio.starting_cash:
        should_stopped = True
    else:
        should_stopped = False

    # 如果有止盈/止损信号，则强制平仓，并结束所有操作
    if should_stopped and current_position > 0:
        # 低于止损线，需要止损
        if context.portfolio.portfolio_value < context.portfolio_stop_loss * context.portfolio.starting_cash:
            print(
                "当前净资产:%.2f 位于止损线下方 (%f), 初始资产:%.2f, 触发止损动作" %
                (context.portfolio.portfolio_value, context.portfolio_stop_loss,
                 context.portfolio.starting_cash))
            context.stop_loss_triggered = True
        # 高于止盈线，需要止盈
        else:
            print(
                "当前净资产:%.2f 位于止盈线上方 (%f), 初始资产:%.2f, 触发止盈动作" %
                (context.portfolio.portfolio_value, context.portfolio_stop_win,
                 context.portfolio.starting_cash))
            context.stop_win_triggered = True

        if context.stop_loss_triggered:
            print("设置 stop_loss_triggered（已触发止损信号）为真")
        else:
            print("设置 stop_win_triggered （已触发止损信号）为真")

        # 需要止盈/止损，卖出全部持仓
        if current_position > 0:
            # 卖出时，全仓清空
            print("止盈/止损，正在卖出==>%d" % current_position)
            order_target_percent(context.asset, 0.0)
            # 复原
            # context.stop_loss_triggered = False
            # context.stop_win_triggered = False
        return

    history = data.history(assets=context.asset,
                           fields=['open', 'high', 'low', 'close', 'volume'],
                           bar_count=context.window_size+1,
                           frequency='1d')

    # 判断读取数量是否正确
    if len(history.index) < (context.window_size + 1):
        print("bar的数量不足, 等待下一根bar...")
        return

    date = history.index.values[-1]

    # 开始计算N日最高价的最高价HH，N日收盘价的最高价HC，N日收盘价的最低价LC，N日最低价的最低价LL
    hh = np.max(history["high"].iloc[-context.window_size-1:-1])
    hc = np.max(history["close"].iloc[-context.window_size-1:-1])
    lc = np.min(history["close"].iloc[-context.window_size-1:-1])
    ll = np.min(history["low"].iloc[-context.window_size-1:-1])
    price_range = max(hh - lc, hc - ll)

    # 取得倒数第二根bar的close, 并计算上下界限
    up_bound = history["open"].iloc[-1] + context.K1 * price_range
    low_bound = history["open"].iloc[-1] - context.K2 * price_range

    # print("当前 价格：%s, 上轨：%s, 下轨: %s" % (current_price, up_bound, low_bound))

    current_position = context.portfolio.positions[context.asset].amount

    # 产生买入卖出信号，并执行操作
    if current_price > up_bound:
        print("价格突破上轨，产生买入信号")
        if context.portfolio.cash >= 0 and current_position <= 0:
            # 买入信号，且持有现金，则市价单全仓买入
            print("正在买入")
            order_target_percent(context.asset, 1.0)
        else:
            print("现金不足，无法下单")
    elif current_price < low_bound:
        print("价格突破下轨，产生卖出信号")
        if current_position > 0:
            # 卖出信号，且持有仓位，则市价单全仓卖出
            print("正在卖出")
            order_target_percent(context.asset, 0.0)
            # order_target(context.asset, -current_position)
        else:
            print("仓位不足，无法卖出")
    else:
        print("无交易信号，进入下一根bar")


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
