import backtrader as bt


# 中轨：20日均线
# 标准差：最近20个收盘价求标准差
# 上轨：20日均线 + 2 × 标准差
# 下轨：20日均线 - 2 × 标准差

# 布林带策略
class BollingerBandStrategy(bt.Strategy):
    params = (
        ('period', 20),  # 布林带周期
        ('devfactor', 2.0)  # 标准差倍数
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(self.datas[0],
                                                 period=self.p.period,
                                                 devfactor=self.p.devfactor)

    def next(self):
        if not self.position:
            # 收盘价下穿下轨, 买入
            if self.datas[0].close[0] < self.boll.bot[0]:
                self.buy()
        else:
            # 收盘价上穿上轨, 卖出
            if self.datas[0].close[0] > self.boll.top[0]:
                self.sell()


# 准备数据
data = bt.feeds.GenericCSVData(dataname='../csv/data_okb.csv',
                               dtformat='%Y-%m-%d %H:%M:%S',
                               timeframe=bt.TimeFrame.Days)

# 创建回测引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(BollingerBandStrategy)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

# 数据源
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.setcash(100000)

# 设置佣金
cerebro.broker.setcommission(commission=0.001)

# 启动回测

result = cerebro.run()
strat = result[0]
drawdown = strat.analyzers.drawdown.get_analysis()
print('最大回撤: ', drawdown['max']['drawdown'])
print('最大回撤百分比: {:.2f}%'.format(drawdown['max']['drawdown']))
print('最大回撤期间持续天数: ', drawdown['max']['len'])

cerebro.plot()