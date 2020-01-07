import pandas as pd
import talib as ta
import numpy as np
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function, order_target_value, order_target
from zipline.utils.events import date_rules, time_rules

"""
网格交易策略
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    # 底仓价格
    context.base_price = None
    # 计算移动均值所需的历史bar数目，用户自定义的变量，可以被handle_data使用
    context.sma_window_size = 24
    # 确定当前price可否作为base_price的依据就是当前price是否小于20日均线*price_to_sma_threshold
    context.price_to_sma_threshold = 1
    # 止损线，用户自定义的变量，可以被handle_data使用
    context.portfolio_stop_loss = 0.90
    # 用户自定义变量，记录下是否已经触发止损
    context.stop_loss_triggered = False
    # 止盈线，用户自定义的变量，可以被handle_data使用
    context.portfolio_stop_win = 1.10
    # 用户自定义变量，记录下是否已经触发止盈
    context.stop_win_triggered = False
    # 设置网格的4个档位的买入价格（相对于基础价的百分比）
    context.buy4, context.buy3, context.buy2, context.buy1 = 0.88, 0.91, 0.94, 0.97
    # 设置网格的4个档位的卖出价格（相对于基础价的百分比）
    context.sell4, context.sell3, context.sell2, context.sell1 = 1.8, 1.6, 1.4, 1.2

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    current_position = context.portfolio.positions[context.asset].amount

    if context.stop_loss_triggered:
        print("已触发止损线, 此bar不会有任何指令 ... ")
        return

    if context.stop_win_triggered:
        print("已触发止盈线, 此bar不会有任何指令 ... ")
        return

    # 检查是否到达止损线或者止盈线，如果是，强制平仓，并结束所有操作
    if context.portfolio.portfolio_value < context.portfolio_stop_loss * context.portfolio.starting_cash or context.portfolio.portfolio_value > context.portfolio_stop_win * context.portfolio.starting_cash:
        should_stopped = True
    else:
        should_stopped = False

    # 如果有止盈/止损信号，则强制平仓，并结束所有操作
    if should_stopped:
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

        # 有止盈/止损，且当前有仓位，则强平所有仓位
        if current_position > 0:
            print("正在卖出 %s" % context.asset)
            order_target_percent(context.asset, 0.0)
        return

    # 获取当前价格
    price = data[context.asset].price
    record(price=price)

    # 设置网格策略基础价格（base_price)
    if context.base_price is None:
        # 获取历史数据, 取后sma_window_size根bar
        history = data.history(context.asset, ['close'], context.sma_window_size, '1d')
        if len(history.index) < context.sma_window_size:
            print("bar的数量不足, 等待下一根bar...")
            return
        # 计算sma均线值
        sma = ta.SMA(history['close'].values, timeperiod=context.sma_window_size)[-1]
        # 若当前价格满足条件，则设置当前价格为基础价
        if price < context.price_to_sma_threshold * sma and context.base_price is None:
            context.base_price = price
            # 在基础价格位置建仓，仓位为50%
            print("建仓中...")
            cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.5, context.portfolio.cash)
            print("正在买入 %s" % context.asset)
            print("下单金额为 %s 元" % cash_to_spent)
            order_target_value(context.asset, cash_to_spent)
            return

    # 还没有找到base_price，则继续找，不着急建仓
    if context.base_price is None:
        print("尚未找到合适的基准价格，进入下一根bar")
        return

    cash_to_spent = 0

    # 计算为达到目标仓位需要买入/卖出的金额
    # 价格低于buy4所对应的价格时，仓位调至100%
    if price / context.base_price < context.buy4:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 1, context.portfolio.cash)
    # 价格大于等于buy4对应的价格，低于buy3所对应的价格时，仓位调至90%
    elif price / context.base_price < context.buy3:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.9, context.portfolio.cash)
    # 价格大于等于buy3对应的价格，低于buy2所对应的价格时，仓位调至70%
    elif price / context.base_price < context.buy2:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.7, context.portfolio.cash)
    # 价格大于等于buy2对应的价格，低于buy1所对应的价格时，仓位调至60%
    elif price / context.base_price < context.buy1:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.6, context.portfolio.cash)
    # 价格大于sell4对应的价格，仓位调至0%
    elif price / context.base_price > context.sell4:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0, context.portfolio.cash)
    # 价格小于等于sell4对应的价格，大于sell3所对应的价格时，仓位调至10%
    elif price / context.base_price > context.sell3:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.1, context.portfolio.cash)
    # 价格小于等于sell3对应的价格，大于sell2所对应的价格时，仓位调至30%
    elif price / context.base_price > context.sell2:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.3, context.portfolio.cash)
    # 价格小于等于sell2对应的价格，大于sell1所对应的价格时，仓位调至40%
    elif price / context.base_price > context.sell1:
        cash_to_spent = cash_to_spent_fn(context.portfolio.portfolio_value, 0.4, context.portfolio.cash)

    # 根据策略调整仓位
    if cash_to_spent > price:
        #  市价单买入一定金额
        print("正在买入 %s" % context.asset)
        print("下单金额为 %s 元" % str(cash_to_spent))
        order_target_value(context.asset, context.portfolio.positions_value + cash_to_spent)
    elif cash_to_spent < 0:
        #  计算需要卖出的数量，并已市价单卖出
        quantity = min(current_position, -1 * cash_to_spent / price)
        if quantity > 1:
            print("正在卖出 %d 股" % int(quantity))
            order_target(context.asset, current_position - int(quantity))


# 计算为达到目标仓位所需要购买的金额
def cash_to_spent_fn(net_asset, target_ratio, available_cny):
    return available_cny - net_asset * (1 - target_ratio)


if __name__ == '__main__':
    start_session = pd.to_datetime('2012-05-01', utc=True)
    end_session = pd.to_datetime('2013-04-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 100000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
