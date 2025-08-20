from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

cerebro = bt.Cerebro()

data = bt.feeds.GenericCSVData(dataname='../csv/data_eth.csv')

print(data)

cerebro.adddata(data)

cerebro.broker.setcash(100000.0)

cerebro.run()
cerebro.plot()