import backtrader as bt

# 双均线策略
class SmaCrossStrategy(bt.Strategy):

    params = dict(
        fast_period=10,
        slow_period=30
    )

    def __init__(self):
        # 定义两条均线
        # 公式： n日SMA = 最近n天收盘价之和 / n
        self.sma_fast = bt.ind.SimpleMovingAverage(self.datas[0], period=self.p.fast_period)
        self.sma_slow = bt.ind.SimpleMovingAverage(self.datas[0], period=self.p.slow_period)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)  # 金叉/死叉

    def next(self):
        if not self.position:
            # 如果尚未持仓，出现金叉则买入
            if self.crossover > 0:
                self.buy()
        else:
            # 如果已有持仓，出现死叉则卖出
            if self.crossover < 0:
                self.sell()

# 创建交易系统
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCrossStrategy)

# 准备数据
data = bt.feeds.GenericCSVData(dataname='../csv/data_okb.csv',
                               dtformat='%Y-%m-%d %H:%M:%S',
                               timeframe=bt.TimeFrame.Days)

cerebro.adddata(data)

# 设置初始资金
cerebro.broker.set_cash(100000)
cerebro.addsizer(bt.sizers.FixedSize, stake=100)

cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

print('初始市值: %.2f' % cerebro.broker.getvalue())
result = cerebro.run()
first_strategy = result[0]
drawdown = first_strategy.analyzers.drawdown.get_analysis()
print('回测后市值: %.2f' % cerebro.broker.getvalue())
print('最大回撤: %.2f%%' % drawdown['max']['drawdown'])



cerebro.plot()