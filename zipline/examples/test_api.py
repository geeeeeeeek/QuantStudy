import pandas as pd
import zipline
from zipline.api import symbol, schedule_function, order_target_percent, set_commission, order_target_value
from zipline.finance import commission
from zipline.utils.events import date_rules, time_rules


def initialize(context):
    context.asset = symbol('IBM')
    set_commission(commission.PerShare(cost=0.0001, min_trade_cost=0))

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close'],
                           bar_count=10,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values
    print("===============================================================")
    print("持仓数 amount=", context.portfolio.positions[symbol('IBM')].amount)
    print("每股成本 cost_basis=", context.portfolio.positions[symbol('IBM')].cost_basis)
    print("最新价格 last_sale_price=", context.portfolio.positions[symbol('IBM')].last_sale_price)
    print("能否交易 can_trade=", data.can_trade(context.asset))
    print("current price=", data.current(context.asset, 'close'))

    print("使用现金 capital_used=", context.portfolio.capital_used)
    print("剩余现金 cash=", context.portfolio.cash)
    print("今日收益 pnl=", context.portfolio.pnl)
    print("收益率 returns=", context.portfolio.returns)
    print("起始现金 starting_cash=", context.portfolio.starting_cash)
    print("总市值 portfolio_value=", context.portfolio.portfolio_value)
    print("持仓市值 positions_value=", context.portfolio.positions_value)

    amount = context.portfolio.positions[symbol('IBM')].amount
    if amount == 0:
        order_id = order_target_value(context.asset, 200)
    else:
        order_id = order_target_value(context.asset, 400)
    print("order_id==>", order_id)


if __name__ == '__main__':
    start_session = pd.to_datetime('2013-01-04', utc=True)
    end_session = pd.to_datetime('2013-01-15', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    # perf.to_pickle("output.pkl")
