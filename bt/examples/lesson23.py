import backtrader as bt


# CCI极值反转策略
# 计算公式：CCI(n)=(TP - MA)÷MD÷0.015
# 原理：突破极值（如±200）并反向回归临界区域时进行顺势或反转操作
# 特点：适合震荡行情，缺点是对趋势行情极为敏感、容易亏损
# 可以配合其它指标减少亏损

class CCIExtremeLong(bt.Strategy):
    params = (
        ('cci_period', 20),
        ('extreme', 200),
    )

    def __init__(self):
        self.cci = bt.indicators.CommodityChannelIndex(period=self.params.cci_period)
        self.prev_cci = None

    def next(self):
        if self.prev_cci is not None:
            # 买入信号：CCI从极低回升
            if self.prev_cci < -self.params.extreme and self.cci[0] > -self.params.extreme:
                if not self.position:
                    self.buy()
            # 平仓信号：CCI从极高回落
            elif self.prev_cci > self.params.extreme and self.cci[0] < self.params.extreme:
                if self.position:
                    self.close()
        self.prev_cci = self.cci[0]


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(CCIExtremeLong)

    data = bt.feeds.GenericCSVData(dataname='../csv/000002.csv',
                                   dtformat='%Y-%m-%d',
                                   timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data)

    cerebro.broker.setcash(100000)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=20)

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
