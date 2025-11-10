from tigeropen.common.consts import (Language,  # 语言
                                     Market,  # 市场
                                     BarPeriod,  # k线周期
                                     QuoteRight)  # 复权类型
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient
import pandas as pd


# 获取k线行情

def get_client_config():
    client_config = TigerOpenClientConfig()
    client_config.private_key = read_private_key('E:\\software\\rsa_key')
    client_config.tiger_id = '20150279'
    client_config.account = '20190425155943480'
    client_config.language = Language.en_US
    return client_config


client_config = get_client_config()

quote_client = QuoteClient(client_config)

# k线
bars = quote_client.get_bars(['AAPL'],
                             period=BarPeriod.DAY,
                             limit=1000,
                             begin_time='2025-06-05 00:30:00',
                             )

print(bars.head())

# 时间格式转换
bars['time'] = pd.to_datetime(bars['time'], unit='ms').dt.strftime('%Y-%m-%d')

bars.to_csv('AAPL_daily_kline.csv', columns=['time', 'open', 'high', 'low', 'close', 'volume'], index=False)
