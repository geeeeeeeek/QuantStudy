import numpy as np
import pandas as pd
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function, order_target_value
from zipline.utils.events import date_rules, time_rules

"""
海龟策略
海龟策略最大的特点并不是获得多大收益而是控制最大回撤，保证本金安全。

唐奇安通道:
上线=Max（前N个交易日的最高价）
下线=Min（前N个交易日的最低价）
中线=（上线+下线）/2

波动幅度均值(ATR)
TrueRange（tr=Max(High−Low,High−PreClose,PreClose−Low)
ATR = TrueRange/n

买卖单位
Unit=账户资金*0.01/ATR

策略步骤：
1. 计算ATR
2. 判断加仓或止损
3. 判断入场或离场
"""


# 用户自定义的函数，可以被handle_data调用:用于初始化一些用户数据
def init_local_context(context):
    # 上一次买入价
    context.last_buy_price = 0
    # 是否持有头寸标志
    context.hold_flag = False
    # 限制最多买入的单元数
    context.limit_unit = 4
    # 现在买入1单元的security数目
    context.unit = 0
    # 买入次数
    context.add_time = 0


# 唐奇安通道计算及判断入场离场
# data是日线级别的历史数据，price是当前分钟线数据（用来获取当前行情），T代表需要多少根日线
def in_or_out(context, data, price, T):
    up = np.max(data["high"].iloc[-T:])
    # 这里是T/2唐奇安下沿，在向下突破T/2唐奇安下沿卖出而不是在向下突破T唐奇安下沿卖出，这是为了及时止损
    down = np.min(data["low"].iloc[-int(T / 2):])
    print("当前价格为: %s, 唐奇安上轨为: %s, 唐奇安下轨为: %s" % (price, up, down))
    # 当前价格升破唐奇安上沿，产生入场信号
    if price > up:
        print("价格突破唐奇安上轨")
        return 1
    # 当前价格跌破唐奇安下沿，产生出场信号
    elif price < down:
        print("价格跌破唐奇安下轨")
        return -1
    # 未产生有效信号
    else:
        return 0


# ATR值计算
def calc_atr(data):
    tr_list = []
    for i in range(len(data)):
        tr = max(data["high"].iloc[i] - data["low"].iloc[i], data["high"].iloc[i] - data["close"].iloc[i - 1],
                 data["close"].iloc[i - 1] - data["low"].iloc[i])
        tr_list.append(tr)
    atr = np.array(tr_list).mean()
    return atr


# 计算unit
def calc_unit(per_value, atr):
    return per_value / atr


# 判断是否加仓或止损:
# 当价格相对上个买入价上涨 0.5ATR时，再买入一个unit; 当价格相对上个买入价下跌 2ATR时，清仓
def add_or_stop(price, lastprice, atr, context):
    if price >= lastprice + 0.5 * atr:
        print("当前价格比上一个购买价格上涨超过0.5个ATR")
        return 1
    elif price <= lastprice - 2 * atr:
        print("当前价格比上一个购买价格下跌超过2个ATR")
        return -1
    else:
        return 0


def initialize(context):
    print("init")
    context.asset = symbol('IBM')

    context.T = 10

    # 自定义的初始化函数
    init_local_context(context)

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(context.asset, ['close', 'high', 'low', 'open'],
                           context.T + 1, '1d')

    # 获取当前持仓数
    current_position = context.portfolio.positions[context.asset].amount
    print("当前持仓数==>%d" % current_position)

    # 获取当前行情数据
    price = data.current(context.asset, 'close')
    record(price=price)

    # 1 计算ATR
    atr = calc_atr(history.iloc[:len(history) - 1])

    # 2 判断加仓或止损
    if context.hold_flag is True and current_position > 0:  # 先判断是否持仓
        temp = add_or_stop(price, context.last_buy_price, atr, context)
        if temp == 1:  # 判断加仓
            if context.add_time < context.limit_unit:  # 判断加仓次数是否超过上限
                print("产生加仓信号")
                cash_amount = min(context.portfolio.cash, context.unit * price)  # 不够1unit时买入剩下全部
                context.last_buy_price = price
                if cash_amount >= price:
                    context.add_time += 1
                    print("正在买入 %s" % context.asset)
                    print("下单金额为 %s 元" % cash_amount)
                    order_target_value(context.asset, context.portfolio.positions_value + cash_amount)
                else:
                    print("订单无效，下单金额小于交易所最小交易金额")
            else:
                print("加仓次数已经达到上限，不会加仓")
        elif temp == -1:  # 判断止损
            # 重新初始化参数！重新初始化参数！重新初始化参数！非常重要！
            init_local_context(context)
            # 卖出止损
            print("产生止损信号")
            print("正在卖出 %s" % context.asset)
            print("卖出数量为 %s" % current_position)
            order_target_percent(context.asset, 0.0)

    # 3 判断入场离场
    else:
        out = in_or_out(context, history.iloc[:len(history) - 1], price, context.T)
        if out == 1:  # 入场
            if context.hold_flag is False:
                value = context.portfolio.cash * 0.01
                context.unit = calc_unit(value, atr)
                print('unit===>%d, atr===>%d' % (context.unit, atr))
                context.add_time = 1
                context.hold_flag = True
                context.last_buy_price = price
                cash_amount = min(context.portfolio.cash, context.unit * price)
                # 有买入信号，执行买入
                print("产生入场信号")
                print("正在买入 %s" % context.asset)
                print("下单金额为 %s 元" % cash_amount)
                order_target_value(context.asset, cash_amount)
            else:
                print("已经入场，不产生入场信号")
        elif out == -1:  # 离场
            if context.hold_flag is True:
                if current_position >= 1:
                    print("产生止盈离场信号")
                    # 重新初始化参数
                    init_local_context(context)
                    # 有卖出信号，且持有仓位，则市价单全仓卖出
                    print("正在卖出 %s" % context.asset)
                    print("卖出数量为 %s" % current_position)
                    order_target_percent(context.asset, 0.0)
            else:
                print("尚未入场或已经离场，不产生离场信号")


if __name__ == '__main__':
    start_session = pd.to_datetime('2014-01-01', utc=True)
    end_session = pd.to_datetime('2014-09-10', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 100000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
