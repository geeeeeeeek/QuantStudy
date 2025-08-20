import backtrader as bt
from datetime import datetime

# 三均线交叉策略优点是简单易懂、适合趋势行情，能长期跑赢部分大势；
# 缺点是滞后性导致无法捕捉全部行情，震荡市时反复亏损。
# 适合长期趋势性明显的市场，不适合横盘震荡时单独使用。
# 实盘可结合其他指标、风控规则，提升有效性。

class ThreeMA(bt.Strategy):
    params = (
        ('fast_period', 5),
        ('mid_period', 20),
        ('slow_period', 60),
    )

    def __init__(self):
        self.ma_fast = bt.ind.SMA(self.datas[0], period=self.p.fast_period)
        self.ma_mid = bt.ind.SMA(self.datas[0], period=self.p.mid_period)
        self.ma_slow = bt.ind.SMA(self.datas[0], period=self.p.slow_period)
        self.crossover = bt.ind.CrossOver(self.ma_fast, self.ma_mid)

    def next(self):
        if not self.position:
            if self.crossover > 0 and self.ma_mid > self.ma_slow:
                self.buy()
        else:
            if self.crossover < 0 and self.ma_mid < self.ma_slow:
                self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ThreeMA)

    # data
    data = bt.feeds.GenericCSVData(dataname='../csv/data_eth.csv',
                                   dtformat='%Y-%m-%d %H:%M:%S',
                                   timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data)
    cerebro.broker.setcash(100000)

    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    print('开始资金: %.2f' % cerebro.broker.getvalue())
    result = cerebro.run()
    strat = result[0]
    dd = strat.analyzers.drawdown.get_analysis()
    print('最大回撤: %.2f%%, 最大金额: %.2f' % (dd['max']['drawdown'], dd['max']['moneydown']))
    print('最终资金: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
