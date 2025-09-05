import backtrader as bt


# RSI超买超卖策略
# 策略逻辑
# RSI低于超卖阈值（如30），认为市场过度下跌，考虑买入
# RSI高于超买阈值（如70），认为市场过度上涨，考虑卖出
# 特点：
# 反转捕捉，震荡有效，趋势无力
# 适合：
# 震荡市/区间盘整：价格在一定区间反复波动时，RSI超买超卖策略比较有效。
# 短线交易：比如日内波段或小周期（15min、1h等）。
# 捕捉小级别反转：如回调反弹、技术修正。
# 不适合：
# 趋势行情：如牛市持续上涨或熊市持续下跌，多次给出反向信号导致亏损。

# 均线策略 布林带策略 联合使用。


class RSI_Strategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        # 计算公式 RSI = 100 - [100 / (1 + 平均上涨幅度 / 平均下跌幅度)]
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.rsi_period)

    def next(self):
        if not self.position:
            # 没有持仓时，若RSI小于阈值，买入
            if self.rsi < self.params.rsi_oversold:
                self.buy()
        else:
            # 持仓中，若RSI大于阈值，卖出
            if self.rsi > self.params.rsi_overbought:
                self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(dataname='../csv/test2.csv',
                                   dtformat='%Y-%m-%d',
                                   timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data)
    cerebro.broker.setcash(100000)

    cerebro.addstrategy(RSI_Strategy)

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
