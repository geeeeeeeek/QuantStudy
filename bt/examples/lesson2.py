import backtrader as bt
import datetime

# 均线策略
class MaCrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.datas[0], period=self.p.fast_period)
        self.slow_ma = bt.indicators.SMA(self.datas[0], period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:
            # 如果均线上穿买入
            if self.crossover > 0:
                self.buy()
        else:
            # 如果均线下穿卖出
            if self.crossover < 0:
                self.sell()


data = bt.feeds.GenericCSVData(dataname='../csv/data_eth.csv')

cerebro = bt.Cerebro()
cerebro.addstrategy(MaCrossStrategy)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

print('初始资金: %.2f' % cerebro.broker.getvalue())
results = cerebro.run()
print('回测结束资金: %.2f' % cerebro.broker.getvalue())

# 输出夏普率
print('Sharpe Ratio:', results[0].analyzers.sharpe.get_analysis())

cerebro.plot()
