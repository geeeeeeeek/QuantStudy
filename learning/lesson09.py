import os

import tushare as ts
import schedule
import time

from learning.send_mail import send_email

token = os.getenv('TUSHARE_TOKEN')

ts.set_token(token)
pro = ts.pro_api()

stock_list = ['000001.SZ', '300033.SZ', '000988.SZ', ]


# 监听股票行情交易信号并自动发邮件提醒

# 连涨信号判断
def check_continuous_up(code, days=3):
    df = pro.daily(ts_code=code, limit=days + 1)
    if df is None or len(df) < days + 1:
        return False
    df = df.sort_values('trade_date')
    cnt = 0
    for i in range(1, days + 1):
        if df.iloc[i]['close'] > df.iloc[i - 1]['close']:
            cnt += 1
        else:
            break
    return cnt == days


def monitor_stocks():
    print(f"执行任务，时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    for code in stock_list:
        if check_continuous_up(code, days=3):
            print(f"{code} 连续上涨3天，发出买入信号！")
            send_email("产生了交易信号", ['285126081@qq.com'], "测试内容",
                       sender_pass="your code")
        else:
            print(f"{code} 未连续上涨3天。")


# 每天固定时间
# schedule.every().day.at("10:00").do(monitor_stocks)

# 或 每隔10秒
schedule.every(10).seconds.do(monitor_stocks)

print("定时监控启动！")
while True:
    schedule.run_pending()
    time.sleep(5)
