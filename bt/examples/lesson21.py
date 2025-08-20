import backtrader as bt


# macd策略实现
# 计算两条指数移动平均线（EMA
# 特点：适合用于中长期、趋势明显的行情，筛选大概率的趋势波段机会，但在震荡市和无明显方向时容易产生噪声信号

class MACDCrossStrategy(bt.Strategy):

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.datas[0],
            period_me1=15,
            period_me2=30,
            period_signal=9
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position and self.crossover[0] > 0:
            self.buy()
        elif self.position and self.crossover[0] < 0:
            self.sell()


# 回测主流程
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACDCrossStrategy)

    data = bt.feeds.GenericCSVData(dataname='../csv/000651.csv',
                                   dtformat='%Y%m%d',
                                   timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data)

    cerebro.broker.set_cash(100000)


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
