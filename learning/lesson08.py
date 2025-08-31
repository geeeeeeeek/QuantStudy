import tushare as ts
import pandas as pd
from sqlalchemy import create_engine

pro = ts.pro_api()

# 股票k线数据保存到mysql数据库


# 获取K线数据
df = pro.daily(ts_code='000001.SZ', start_date='20250101', end_date='20250601')
print(df.head())

# MySQL连接
user = 'root'
password = '4643830'
host = 'localhost'
port = 3306
database = 'stock_db'
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4")

# 保存数据
df_select = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']]
df_select.to_sql('kline', engine, if_exists='append', index=False)
