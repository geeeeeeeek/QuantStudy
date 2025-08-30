import tushare as ts
import pandas as pd

# 采集股票数据保存到excel

pro = ts.pro_api()

# 获取K线数据
df = pro.daily(ts_code='000001.SZ', start_date='20250101', end_date='20250601')
print(df.head())

# 导出到excel
df.to_excel('000001.xlsx', index=False)
