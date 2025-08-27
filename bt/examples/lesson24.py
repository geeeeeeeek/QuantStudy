import backtrader as bt
from datetime import datetime


# ATR极值反转策略，本质是利用ATR（Average True Range，均幅指标）衡量市场波动
# 市场的心情：恐慌/冷静
# 优点：简单、能识别极端波动、适合震荡市；
# 缺点：趋势市易亏，ATR非方向指标，易于误判；
# 适用场景：波动性高、无明显趋势的市场，建议结合其他过滤指标辅助用。

# TR = max(当日最高-当日最低, abs(当日最高-昨日收盘), abs(当日最低-昨日收盘))
# ATR = TR的N日均值

class ATRReversalStrategy(bt.Strategy):
    params = (
        ('atr_period', 14),
        ('extreme_period', 20),
    )

    def __init__(self):
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.max_atr = bt.ind.Highest(self.atr, period=self.p.extreme_period)
        self.min_atr = bt.ind.Lowest(self.atr, period=self.p.extreme_period)
        self.bar_executed = None  # 记录建仓的bar号
        self.order = None

    def next(self):
        if not self.position:
            #  做空
            if self.atr[0] > self.max_atr[-1]:
                self.order = self.sell()
                print(f'ATR极高，做空，日期: {self.data.datetime.date(0)}, ATR: {self.atr[0]:.2f}')
            #  做多
            elif self.atr[0] < self.min_atr[-1]:
                self.order = self.buy()
                print(f'ATR极低，做多，日期: {self.data.datetime.date(0)}, ATR: {self.atr[0]:.2f}')
        else:
            # 平仓条件：持有N天后离场
            if self.bar_executed is not None and (len(self) - self.bar_executed) >= self.p.extreme_period:
                self.close()
                print(f'平仓! 日期: {self.data.datetime.date(0)}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy() or order.issell():
                self.bar_executed = len(self)   # 记录建仓bar编号
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ATRReversalStrategy)
    data = bt.feeds.GenericCSVData(dataname='../csv/000002.csv',
                                   dtformat='%Y-%m-%d',
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

    # 打印胜率
    tradeanalyzer = strategy.analyzers.tradeanalyzer.get_analysis()
    total_trades = tradeanalyzer.total.closed if 'closed' in tradeanalyzer.total else 0
    won_trades = tradeanalyzer.won.total if 'won' in tradeanalyzer and 'total' in tradeanalyzer.won else 0
    winrate = (won_trades / total_trades) * 100 if total_trades > 0 else 0
    print(f"总交易数: {total_trades}")
    print(f"盈利交易数: {won_trades}")
    print(f"胜率: {winrate:.2f}%")
    cerebro.plot()