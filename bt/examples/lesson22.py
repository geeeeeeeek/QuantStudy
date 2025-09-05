
# RSI + 均线 联合策略
# 兼顾趋势和震荡
# 均线（MA）捕捉的是趋势、方向性行情，RSI则擅长判断超买/超卖、震荡区间。
# 两者联合，可以过滤掉趋势中的虚假震荡信号，也能防止趋势追高/杀跌。

import backtrader as bt


class MaRsiStrategy(bt.Strategy):
    params = (
        ('ma_period', 20),
        ('rsi_period', 14),
        ('rsi_buy', 40),
        ('rsi_sell', 60),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period)
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.rsi_period)

    def next(self):
        # 买入条件
        if not self.position:
            if (self.data.close[0] > self.sma[0] and self.data.close[-1] <= self.sma[-1] and
                    self.rsi[0] > self.params.rsi_buy >= self.rsi[-1]):
                self.buy()
                print(f'买入 价格 {self.data.close[0]}, 日期: {self.datas[0].datetime.date(0)}')
        else:
            # 卖出条件
            if (self.data.close[0] < self.sma[0] and self.data.close[-1] >= self.sma[-1] and
                    self.rsi[0] < self.params.rsi_sell <= self.rsi[-1]):
                self.sell()
                print(f'卖出 价格 {self.data.close[0]}, 日期: {self.datas[0].datetime.date(0)}')


# ====== 回测流程（以csv文件为例） =======
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(dataname='../csv/test2.csv',
                                   dtformat='%Y-%m-%d',
                                   timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data)
    cerebro.addstrategy(MaRsiStrategy)
    cerebro.broker.set_cash(100000)
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

    # 可视化
    cerebro.plot()