import pandas as pd
import talib as ta
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
RSI为相对强弱指数(Relative Strength Index)
是通过比较一段时期内一只个股的平均收盘涨数和平均收盘跌数来分析市场买卖盘的意向和实力
RSI = 100×RS/(1+RS) 或者，RSI=100－100÷（1+RS）
其中 RS=14天内收市价上涨数之和的平均值/14天内收市价下跌数之和的平均值 
RSI指标值：0-100
80—100极强卖出 
50—80强买入
 20—50弱观望 
0—20极弱买入
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')

    # 止损线
    context.portfolio_stop_loss = 0.9
    # 止盈线
    context.portfolio_stop_win = 1.1
    # 是否已经触发止损
    context.stop_loss_triggered = False
    # 是否已经触发止盈
    context.stop_win_triggered = False
    # 买入线
    context.lower_rsi = 30
    # 卖出线
    context.upper_rsi = 80
    # 历史长度
    context.rsi_window = 21

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    record(price=data[context.asset].price)
    current_position = context.portfolio.positions[context.asset].amount
    print("持仓数=%d" % current_position)

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
        return

    # RSI策略逻辑
    history = data.history(context.asset, ['close'], context.rsi_window + 1, '1d')
    date = history.index.values[-1]
    close = history['close'].values

    # 计算RSI
    rsi = ta.RSI(close, context.rsi_window)

    buy_signal_triggered = False
    sell_signal_triggered = False

    price = data.current(context.asset, 'close')
    record(price=price)

    if rsi[-1] < context.lower_rsi:
        buy_signal_triggered = True
    if rsi[-1] > context.upper_rsi:
        sell_signal_triggered = True

    current_position = context.portfolio.positions[context.asset].amount

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>买入信号')
        order_target_percent(context.asset, 1.0)

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>卖出信号')
        order_target_percent(context.asset, 0.0)
    else:
        print(str(date) + '==>无交易信号')


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
