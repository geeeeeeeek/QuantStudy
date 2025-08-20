import backtrader as bt
import pandas as pd


class KDJStrategy(bt.Strategy):
    params = (
        ('rsv_period', 9),  # RSV 计算周期
        ('k_period', 3),  # K 值平滑周期
        ('d_period', 3),  # D 值平滑周期
    )

    def __init__(self):
        # 计算 RSV
        highest_high = bt.ind.Highest(self.data.high, period=self.params.rsv_period)
        lowest_low = bt.ind.Lowest(self.data.low, period=self.params.rsv_period)
        rsv = (self.data.close - lowest_low) / (highest_high - lowest_low) * 100

        # 计算 K 值和 D 值
        self.k = bt.indicators.EMA(rsv, period=self.params.k_period)
        self.d = bt.indicators.EMA(self.k, period=self.params.d_period)

        # 计算 J 值
        self.j = 3 * self.k - 2 * self.d

    def next(self):
        # 检查 K 值超过 D 值，且 J 值接近低点
        if not self.position and self.k[-1] < self.d[-1] and self.k[0] > self.d[0] and self.j[0] < 20:
            self.buy()  # 买入

        # 检查 D 值超过 K 值，且 J 值接近高点
        if self.position.size > 0 and self.k[-1] > self.d[-1] and self.k[0] < self.d[0] and self.j[0] > 80:
            self.sell()  # 卖出


# 加载数据
if __name__ == '__main__':
    # 创建一个回测平台
    cerebro = bt.Cerebro()

    data = bt.feeds.GenericCSVData(
        dataname='../csv/data_okb.csv',
        dtformat='%Y-%m-%d %H:%M:%S',
        timeframe=bt.TimeFrame.Days
    )
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(KDJStrategy)

    # 运行回测
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 可视化结果
    cerebro.plot()

    # 特点：
    # KDJ反转策略适合短线高频交易者，尤其是在震荡市场中表现最佳。
    # 它对趋势性判断能力较弱，容易受到假信号的影响。
