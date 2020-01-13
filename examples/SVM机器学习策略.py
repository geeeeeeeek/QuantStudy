import talib
import pandas as pd
import zipline
from sklearn import svm
from trading_calendars import get_calendar
from zipline.api import symbol, order_target_value, order_target_percent, record, set_benchmark, schedule_function
from zipline.data import bundles
from zipline.data.data_portal import DataPortal
from zipline.utils.events import date_rules, time_rules
import warnings
warnings.filterwarnings("ignore")

"""
基于SVM的机器学习策略
步骤：
1.数据采集
2.训练
3.预测
"""


# 全局参数
train_start_day = '2012-4-10'
train_end_day = '2012-12-10'
calendar_name = "NYSE"
train_symbol_str = "IBM"


def get_window_price(end_date):
    bundle_name = "custom-csv-bundle"
    window = 30  # 窗口大小

    bundle_data = bundles.load(bundle_name)
    data_por = DataPortal(bundle_data.asset_finder,
                          get_calendar(calendar_name),
                          bundle_data.equity_daily_bar_reader.first_trading_day,
                          equity_minute_reader=bundle_data.equity_minute_bar_reader,
                          equity_daily_reader=bundle_data.equity_daily_bar_reader,
                          adjustment_reader=bundle_data.adjustment_reader)

    sym = data_por.asset_finder.lookup_symbol(train_symbol_str, end_date)
    data = data_por.get_history_window(assets=[sym],
                                       end_dt=end_date,
                                       bar_count=window,
                                       frequency='1d',
                                       data_frequency='daily',
                                       field="close")

    close = data.iloc[:, 0].values
    return close


def initialize(context):

    context.asset = symbol('IBM')
    SVM_train(context)

    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


# SVM训练分类器
def SVM_train(context):
    print("开始训练")
    first_day = pd.Timestamp(train_start_day, tz='utc')
    last_day = pd.Timestamp(train_end_day, tz='utc')
    cal = get_calendar(calendar_name)
    days = cal.sessions_in_range(first_day, last_day)

    x_train = []  # 特征
    y_train = []  # 标记

    for day in days:
        close = get_window_price(day)
        # 计算指标
        sma_data = talib.SMA(close)[-1]
        wma_data = talib.WMA(close)[-1]
        mom_data = talib.MOM(close)[-1]

        features = []
        features.append(sma_data)
        features.append(wma_data)
        features.append(mom_data)

        label = False  # 标记为跌(False)
        if close[-1] > close[-2]:  # 如果今天的收盘价超过了昨天，那么标记为涨(True)
            label = True
        x_train.append(features)
        y_train.append(label)

    context.svm_module = svm.SVC()
    context.svm_module.fit(x_train, y_train)  # 训练分类器
    print("训练结束")


def rebalance(context, data):
    history = data.history(context.asset, ['close'], 40, '1d')
    close = history['close'].values
    date = history.index.values[-1]
    current_position = context.portfolio.positions[context.asset].amount
    print("当前持仓==>%d" % current_position)
    price = data[context.asset].price
    record(price=price)

    # 计算指标
    sma_data = talib.SMA(close)[-1]
    wma_data = talib.WMA(close)[-1]
    mom_data = talib.MOM(close)[-1]

    # 添加今日的特征
    features = []
    x = []
    features.append(sma_data)
    features.append(wma_data)
    features.append(mom_data)
    x.append(features)
    flag = context.svm_module.predict(x)  # 预测的涨跌结果

    if bool(flag) and current_position == 0:
        order_target_percent(context.asset, 0.5)
        print(str(date) + "==>买入信号")
    elif bool(flag) is False and current_position > 0:
        order_target_percent(context.asset, 0.0)
        print(str(date) + "==>卖出信号")
    else:
        print(str(date) + "==>无交易信号")


if __name__ == '__main__':
    start_session = pd.to_datetime('2014-01-01', utc=True)
    end_session = pd.to_datetime('2014-10-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
