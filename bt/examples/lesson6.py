from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform
import warnings

import backtrader as bt

warnings.filterwarnings('ignore')
# 单向
class TurtleStrategy(bt.Strategy):
    # 默认参数
    params = (('long_period', 20),
              ('short_period', 10),
              ('printlog', True),)

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.buy_size = 0
        self.buy_count = 0
        # 海龟交易法则中的唐奇安通道和平均波幅ATR
        self.H_line = bt.indicators.Highest(self.data.high(-1), period=self.p.long_period)
        self.L_line = bt.indicators.Lowest(self.data.low(-1), period=self.p.short_period)
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))
        self.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=14)
        # 价格与上下轨线的交叉
        self.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.sell_signal = bt.ind.CrossOver(self.data.close(0), self.L_line)


    def next(self):
        if self.order:
            return
            # 入场：价格突破上轨线且空仓时
        if self.buy_signal > 0 and self.buy_count == 0:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.buy_count = 1
            self.order = self.buy()
            # 加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] and self.buy_count > 0 and self.buy_count <= 4:
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            self.buy_count += 1
            # 离场：价格跌破下轨线且持仓时
        elif self.sell_signal\
                < 0 and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0
            # 止损：价格跌破买入价的2个ATR且持仓时
        elif self.data.close < (self.buyprice - 2 * self.ATR[0]) and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0

            # 交易记录日志（默认不打印结果）

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
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                数量:{order.executed.size},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                数量:{order.executed.size},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败' + str(order.status))
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})； \
        期末总资金: {self.broker.getvalue():.2f}', doprint=True)

class TradeSizer(bt.Sizer):
    params = (('stake', 500),)
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return self.p.stake
        position = self.broker.getposition(data)
        if not position.size:
            return 0
        else:
            return position.size

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TurtleStrategy)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(dataname='../csv/data_okb.csv',
                                   dtformat='%Y-%m-%d %H:%M:%S',
                                   timeframe=bt.TimeFrame.Minutes,)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(50000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(TradeSizer)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0007)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
