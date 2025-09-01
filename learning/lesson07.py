import os
import tushare as ts

token = os.getenv('TUSHARE_TOKEN')

# 采集股票数据保存到excel
ts.set_token(token)
pro = ts.pro_api()

# 获取K线数据
df = pro.daily(ts_code='000001.SZ', start_date='20250101', end_date='20250601')
print(df.head())

# 导出到excel
df = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']]
df.to_excel('000001.xlsx', index=False)
