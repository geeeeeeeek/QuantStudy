import backtrader as bt


# 当价格下穿布林带下轨时，认为价格被低估，有望反弹，发出买入信号；
# 当价格上穿布林带上轨时，认为价格被高估，有望回落，发出卖出/平仓信号。
# 布林带回归策略本质是对市场“过度”波动后的反向操作，适合震荡阶段，但在趋势行情中容易失效。

class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2),
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(
            self.datas[0],
            period=self.params.period,
            devfactor=self.params.devfactor
        )

    def next(self):
        if not self.position:
            # 买入条件：收盘价低于下轨
            if self.data.close < self.boll.lines.bot:
                self.buy()
        else:
            # 卖出条件：收盘价高于上轨
            if self.data.close > self.boll.lines.top:
                self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BollingerBandsStrategy)

    data = bt.feeds.GenericCSVData(dataname='../csv/000651.csv',
                                   dtformat='%Y%m%d',
                                   timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data)

    cerebro.broker.setcash(10000)

    # 添加分析器
    # 最大回撤
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    # 交易分析（胜率）
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')

    print('初始资金: %.2f' % cerebro.broker.getvalue())
    result = cerebro.run()
    strat = result[0]

    # 打印最大回撤
    dd = strat.analyzers.drawdown.get_analysis()
    print('最大回撤: %.2f%%' % dd['max']['drawdown'])

    # 打印胜率
    ta = strat.analyzers.ta.get_analysis()
    if ta.get('total', {}).get('closed', 0):
        won = ta['won']['total'] if 'won' in ta else 0
        lost = ta['lost']['total'] if 'lost' in ta else 0
        total = won + lost
        win_rate = won / total if total > 0 else 0
        print('胜率: %.2f%%' % (win_rate * 100))
    else:
        print('没有交易记录，无法计算胜率')

    print('最终资金: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
