import akshare as ak

# 获取A股k线行情

df = ak.stock_zh_a_daily(symbol="sz000001", start_date="20150601", end_date="20220601")
df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
df = df.rename(columns={'date': 'datetime'})
df['openinterest'] = 0
df.to_csv('../csv/000001.csv', index=False)