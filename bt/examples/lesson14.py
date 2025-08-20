import backtrader as bt
from datetime import datetime

# 盲目跟风型策略
# 动量策略适用于有明显趋势或板块轮动的市场，
# 优点是简单高效、历史业绩好，但缺点是回撤大、容易失效、交易成本高。
# 适合高频交易
# 不太适用场景：
# 持续震荡、没有明显趋势的市场；
# 事件驱动型突发大变盘；
# 交易成本居高不下的品种。

class MomentumStrategy(bt.Strategy):
    params = (
        ('lookback', 60),
    )

    def __init__(self):

        self.mom = bt.ind.Momentum(self.data.close, period=self.p.lookback)

    def next(self):
        if not self.position:
            if self.mom[0] > 0:
                self.buy()
        else:
            if self.mom[0] <= 0:
                self.close()


if __name__ == '__main__':
    data = bt.feeds.GenericCSVData(dataname='../csv/data_okb.csv',
                                   dtformat='%Y-%m-%d %H:%M:%S',
                                   timeframe=bt.TimeFrame.Days)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MomentumStrategy, lookback=60)
    cerebro.adddata(data)
    cerebro.broker.set_cash(100000)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    # 加入最大回撤分析器
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    print('初始资金: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]

    print('回测结束资金: %.2f' % cerebro.broker.getvalue())

    # 打印最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print('最大回撤: {:.2f}%'.format(drawdown.max.drawdown))
    print('最大资金回撤额: {:.2f}'.format(drawdown.max.moneydown))

    cerebro.plot()
