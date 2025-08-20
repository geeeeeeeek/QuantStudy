from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


# Import the backtrader platform


# 支持双向交易

class TurtleStrategy(bt.Strategy):
    # 默认参数
    params = (('long_period', 20),
              ('short_period', 10),
              ('atr_period', 14),
              ('size', 0.1),
              ('printlog', True),)

    def __init__(self):
        self.order = None

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

        # 海龟交易法则中的唐奇安通道和平均波幅ATR
        self.H_line = bt.indicators.Highest(self.data.high(-1), period=self.p.long_period)
        self.L_line = bt.indicators.Lowest(self.data.low(-1), period=self.p.short_period)
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))
        self.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=self.p.atr_period)
        # 价格与上下轨线的交叉
        self.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.sell_signal = bt.ind.CrossOver(self.data.close(0), self.L_line)

    def next(self):

        # 平多
        if self.sell_signal < 0 and self.buy_count > 0:
            self.sellAll()

        # 平空
        if self.buy_signal > 0 and self.sell_count > 0:
            self.buyAll()

        # 做多
        if self.buy_signal > 0 and self.buy_count == 0:
            # time.sleep(0.2)
            self.buy_count = 1
            self.order = self.buy(size=self.p.size)
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] and self.buy_count > 0 and self.buy_count <= 3:
            self.order = self.buy(size=self.p.size)
            self.buy_count += 1

        # 做空
        elif self.sell_signal < 0 and self.sell_count == 0:
            # time.sleep(0.2)
            self.sell_count = 1
            self.order = self.sell(size=self.p.size)
            # 加仓：价格下跌了了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close < self.sellprice - 0.5 * self.ATR[0] and self.sell_count > 0 and self.sell_count <= 3:
            self.order = self.sell(size=self.p.size)
            self.sell_count += 1
    #
    #     # 做多止损
    #     elif self.data.close < (self.buyprice - 2 * self.ATR[0]) and self.buy_count > 0:
    #         print('做多止损..........')
    #         self.sellAll()
    #
    #     # 做空止损
    #     elif self.data.close > (self.sellprice + 2 * self.ATR[0]) and self.sell_count > 0:
    #         print('做空止损..........')
    #         self.buyAll()
    #


    def sellAll(self):
        if self.buy_count > 0:
            position = self.getposition()
            self.sell(size=position.size)
            self.buy_count = 0
            self.buyprice = 0


    def buyAll(self):
        if self.sell_count > 0:
            position = self.getposition()
            self.buy(size=position.size)
            self.sell_count = 0
            self.sellprice = 0

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if not order.isbuy():
                self.log(f'卖出:\n价格:{order.executed.price},\
                数量:{order.executed.size},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.sellprice = order.executed.price
                self.sellcomm = order.executed.comm
            else:
                self.log(f'买入:\n价格：{order.executed.price},\
                数量:{order.executed.size},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})； \
        期末总资金: {self.broker.getvalue():.2f}', doprint=True)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TurtleStrategy)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(dataname='../csv/data_eth.csv',
                                   dtformat='%Y-%m-%d %H:%M:%S',
                                   timeframe=bt.TimeFrame.Days)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(TradeSizer)

    # Set the commission
    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
