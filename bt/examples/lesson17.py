import backtrader as bt
from datetime import datetime


# 均值回归策略
# 核心思想是资产价格在短期内偏离其历史均值后，最终将回归到均值附近。
# sma = n天的收盘价和/n
# 特点：适合震荡行情市场，不适合趋势明显行情市场

class MeanReversionStrategy(bt.Strategy):
    params = (('period', 30), ('dev', 0.05),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.datas[0].close, period=self.params.period)

    def next(self):
        close = self.datas[0].close[0]
        sma = self.sma[0]
        if close > sma * (1 + self.params.dev):
            if not self.position:
                self.sell()
        elif close < sma * (1 - self.params.dev):
            if not self.position:
                self.buy()
        elif self.position:
            if abs(close - sma) < sma * self.params.dev / 2:
                self.close()


cerebro = bt.Cerebro()
cerebro.addstrategy(MeanReversionStrategy)

data = bt.feeds.GenericCSVData(dataname='../csv/000651.csv',
                               dtformat='%Y%m%d',
                               timeframe=bt.TimeFrame.Days)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

# 添加分析器
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years, _name='timereturn')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
print('回测初始资金: %.2f' % cerebro.broker.getvalue())
results = cerebro.run()
strategy = results[0]
print('回测结束资金: %.2f' % cerebro.broker.getvalue())
# 打印最大回撤
dd = strategy.analyzers.drawdown.get_analysis()
print(f"最大回撤: {dd['max']['drawdown']:.2f}%")
print(f"最大回撤金额: ${dd['max']['moneydown']:.2f}")

# 打印年化收益
tr = strategy.analyzers.timereturn.get_analysis()
for year, ret in tr.items():
    print(f"{year} 年年化收益率: {ret * 100:.2f}%")

# 打印胜率
tradeanalyzer = strategy.analyzers.tradeanalyzer.get_analysis()
total_trades = tradeanalyzer.total.closed if 'closed' in tradeanalyzer.total else 0
won_trades = tradeanalyzer.won.total if 'won' in tradeanalyzer and 'total' in tradeanalyzer.won else 0
winrate = (won_trades / total_trades) * 100 if total_trades > 0 else 0
print(f"总交易数: {total_trades}")
print(f"盈利交易数: {won_trades}")
print(f"胜率: {winrate:.2f}%")

cerebro.plot()
