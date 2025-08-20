from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform
import warnings

import backtrader as bt
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')


class TurtleStrategy(bt.Strategy):

    def __init__(self):
        self.order = None

        self.index = 0

        # 做多参数
        self.buyprice = 0
        self.buycomm = 0
        self.buy_size = 0
        self.buy_count = 0

        # 做空参数
        self.sellprice = 0
        self.sellcomm = 0
        self.sell_size = 0
        self.sell_count = 0

        self.ATR_T = 14
        self.T = 20
        self.csv_data = pd.read_csv("../csv/data_eth.csv")

    def next(self):
        self.index += 1
        broker_value = self.broker.getvalue()  # 当前净值
        position_size = self.getposition().size  # 当前持有

        data = self.csv_data[0: self.index]

        """"""""""""""""""""""""" 核心代码 """""""""""""""""""""""""

        price = data.close.iloc[-1]
        signal = in_or_out(data[:-1], price, self.T)
        atr = calc_atr(data, self.ATR_T)

        # 平多
        if signal == -1 and self.buy_count > 0:
            self.sellAll(position_size)
            self.log("平多..." + str(position_size))

        # 平空
        if signal == 1 and self.sell_count > 0:
            self.buyAll(position_size)
            self.log("平空..." + str(position_size))

        # 做多
        if signal == 1 and self.buy_count == 0:
            unit = calc_size(broker_value, price)
            self.order = self.buy(size=unit)
            self.buy_count = 1
            self.buyprice = price
            self.log("做多..." + str(unit))
        # 做多加仓
        elif price > self.buyprice + 0.5 * atr and self.buy_count > 0 and self.buy_count <= 3:
            unit = calc_size(broker_value, price)
            self.order = self.buy(size=unit)
            self.buy_count += 1
            self.buyprice = price
            self.log("做多加仓..." + str(unit))
        # 做空
        elif signal == -1 and self.sell_count == 0:
            unit = calc_size(broker_value, price)
            self.order = self.sell(size=unit)
            self.sell_count = 1
            self.sellprice = price
            self.log("做空..." + str(unit))
        # 做空加仓
        elif price < self.sellprice - 0.5 * atr and self.sell_count > 0 and self.sell_count <= 3:
            unit = calc_size(broker_value, price)
            self.order = self.sell(size=unit)
            self.sell_count += 1
            self.sellprice = price
            self.log("做空加仓..." + str(unit))



    def sellAll(self, size):
        if self.buy_count > 0:
            self.sell(size=size)
            self.buy_count = 0
            self.buyprice = 0


    def buyAll(self, size):
        if self.sell_count > 0:
            self.buy(size=size)
            self.sell_count = 0
            self.sellprice = 0

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()},{txt}')

    def stop(self):
        self.log(f'期末总资金: {self.broker.getvalue():.2f}')


def in_or_out(data, price, T):
    up = np.max(data["high"].iloc[-T:])
    down = np.min(data["low"].iloc[-int(T / 2):])
    if price > up:
        return 1
    elif price < down:
        return -1
    else:
        return 0


# ATR值计算
def calc_atr(vdata, ATR_T):
    tr_list = []
    data = vdata[-ATR_T:] if len(vdata) > ATR_T else vdata
    for i in range(1, len(data)):
        tr = max(data["high"].iloc[i] - data["low"].iloc[i],
                 abs(data["high"].iloc[i] - data["close"].iloc[i - 1]),
                 abs(data["close"].iloc[i - 1] - data["low"].iloc[i]))
        tr_list.append(tr)
    atr = np.array(tr_list).mean()
    return atr


def calc_size(value, price):
    return value * 0.1 / price


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TurtleStrategy)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(dataname='../csv/data_eth1.csv',
                                   dtformat='%Y-%m-%d %H:%M:%S',
                                   timeframe=bt.TimeFrame.Minutes, )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(50000.0)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0007)

    # Print out the starting conditions
    print('初始资金: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('期末资金: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
