import backtrader as bt
from datetime import datetime


class ADXTrendStrategy(bt.Strategy):
    params = (
        ('adx_period', 14),
        ('adx_thresh', 25),
    )

    def __init__(self):
        self.adx = bt.indicators.ADX(self.data, period=self.p.adx_period)
        self.plus_di = bt.indicators.PlusDI(self.data, period=self.p.adx_period)
        self.minus_di = bt.indicators.MinusDI(self.data, period=self.p.adx_period)

    def next(self):
        if not self.position:
            if self.adx[0] > self.p.adx_thresh:
                if self.plus_di[0] > self.minus_di[0]:
                    self.buy()
                elif self.minus_di[0] > self.plus_di[0]:
                    self.sell()
        else:
            if self.position.size > 0:
                if self.minus_di[0] > self.plus_di[0] and self.adx[0] > self.p.adx_thresh:
                    self.close()
            elif self.position.size < 0:
                if self.plus_di[0] > self.minus_di[0] and self.adx[0] > self.p.adx_thresh:
                    self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ADXTrendStrategy)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')   # 添加收益分析器

    data = bt.feeds.GenericCSVData(
        dataname='../csv/data_okb.csv',
        dtformat='%Y-%m-%d %H:%M:%S',
        timeframe=bt.TimeFrame.Days
    )
    cerebro.adddata(data)

    cerebro.broker.set_cash(100000)
    results = cerebro.run()
    strat = results[0]

    # 打印最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print('最大回撤: {:.2f}%'.format(drawdown['max']['drawdown']))

    # 打印总盈亏率（累计收益率）
    returns = strat.analyzers.returns.get_analysis()
    print('总盈亏率: {:.2f}%'.format(returns['rtot'] * 100))

    # 要打印年化收益率用：
    print('年化收益率: {:.2f}%'.format(returns['rnorm'] * 100))

    cerebro.plot()

# 优点：
# 能有效避免区间震荡期的假信号，识别强烈趋势顺势交易；
# 方向判别直观明确。
# 缺点：
# 横盘震荡时可能信号较少；
# 择时入场可能滞后于趋势启动，适合中线或波段顺势策略。


# ADX趋势判断策略的核心逻辑
# 基本策略逻辑如下：
#
# 判断趋势强度：
#
# ADX值大于设定阈值（如25）：市场有明显趋势；
# ADX值低于阈值：市场无明显趋势，容易震荡，不宜进场；
# 判断趋势方向：
#
# +DI > -DI：代表上涨趋势更强，考虑做多；
# -DI > +DI：代表下跌趋势更强，考虑做空。
# 综合条件：
#
# 买入/做多条件：ADX > 阈值且+DI > -DI
# 卖出/做空条件：ADX > 阈值且-DI > +DI
