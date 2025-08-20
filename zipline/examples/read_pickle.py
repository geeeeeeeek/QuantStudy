import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def to_percent(temp, position):
    return '%.2f' % (100 * temp) + '%'


def analyze(perf):
    print(perf.iloc[-1])

    fig = plt.figure()

    # 绘制持仓市值
    ax1 = fig.add_subplot(311)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')

    # 绘制价格
    ax2 = fig.add_subplot(312)
    perf['price'].plot(ax=ax2)

    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[[t[0]['amount'] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.price.loc[buys.index], '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.price.loc[sells.index], 'v', markersize=10, color='k')
    ax2.set_ylabel('price')

    # 绘制收益率
    ax3 = fig.add_subplot(313)
    perf['benchmark_period_return'].plot(ax=ax3)
    perf['algorithm_period_return'].plot(ax=ax3)
    ax3.set_ylabel('period_return')
    ax3.yaxis.set_major_formatter(FuncFormatter(to_percent))

    plt.legend(loc=0)
    plt.show()


if __name__ == '__main__':
    perf = pd.read_pickle('output.pkl')  # read pkl
    analyze(perf)
