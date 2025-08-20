import backtrader as bt
import talib
import numpy as np


# =====================SAR抛物线转向策略==================
# 策略原理：
# 买入信号： 当SAR点位从价格上方转到价格下方，认为下跌结束，开始上涨，发出做多（买入）信号。
# 卖出信号： 当SAR点位从价格下方转到价格上方，认为上涨结束，开始下跌，发出做空（卖出）信号。
# 优缺点：
# 优点：能较早捕捉趋势转折，信号明确。
# 缺点：震荡行情中往往频繁反转，容易产生假信号（摆动收益损失）。

# SARₜ₊₁ = SARₜ + AF × (EPₜ - SARₜ)

class SARTALIB(bt.Indicator):
    lines = ('sar',)
    params = (('acceleration', 0.02), ('maximum', 0.2))

    def __init__(self):
        pass

    def next(self):
        high = np.array(self.datas[0].high.get(size=len(self.datas[0])))
        low = np.array(self.datas[0].low.get(size=len(self.datas[0])))

        if len(high) < 2:
            self.lines.sar[0] = self.datas[0].close[0]
            return

        sar_arr = talib.SAR(
            high,
            low,
            acceleration=self.p.acceleration,
            maximum=self.p.maximum
        )

        self.lines.sar[0] = sar_arr[-1]


class SARTurnStrategy(bt.Strategy):
    params = (('acceleration', 0.02), ('maximum', 0.2))

    def __init__(self):
        self.sar = SARTALIB(acceleration=self.p.acceleration,
                            maximum=self.p.maximum)
        self.crossup = bt.ind.CrossUp(self.datas[0].close, self.sar)
        self.crossdown = bt.ind.CrossDown(self.datas[0].close, self.sar)

    def next(self):
        if not self.position:
            # 入场条件：价格上穿SAR指标
            if self.crossup[0]:
                self.buy()
        else:
            # 出场条件：价格下穿SAR指标
            if self.crossdown[0]:
                self.sell()


if __name__ == '__main__':
    data = bt.feeds.GenericCSVData(
        dataname='../csv/data_okb.csv',
        dtformat='%Y-%m-%d %H:%M:%S',
        timeframe=bt.TimeFrame.Days)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(SARTurnStrategy, acceleration=0.02, maximum=0.2)
    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.001)
    print('回测初始资金: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')

    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')

    results = cerebro.run()
    strat = results[0]

    print('回测结束资金: %.2f' % cerebro.broker.getvalue())

    # 最大回撤
    maxdd = strat.analyzers.drawdown.get_analysis()['max']['drawdown']
    print('最大回撤: %.2f%%' % maxdd)

    ar_dict = strat.analyzers.annual_return.get_analysis()
    # 计算总年化收益，或各年分别打印
    try:
        # 直接打印每个年度收益
        for year, ret in ar_dict.items():
            print(f'{year}年年化收益率: {ret * 100:.2f}%')
        # 也可以用最后一年或平均值作为参考
        if len(ar_dict) > 0:
            avg_ar = sum(ar_dict.values()) / len(ar_dict)
            print('平均年化收益率: %.2f%%' % (avg_ar * 100))
    except Exception as e:
        print('年化收益率无法计算！')

    # 胜率
    ta_dict = strat.analyzers.trade_analyzer.get_analysis()
    won = ta_dict.get('won', {}).get('total', 0)
    total = ta_dict.get('total', {}).get('total', 0)
    winrate = (won / total * 100) if total > 0 else 0.0
    print('胜率: %.2f%%' % winrate)

    cerebro.plot()