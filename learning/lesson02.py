import requests
import pandas as pd


def get_kline(stock_code, market='0', klt=101, fqt=1, begin=0, end=20500000):
    """
    stock_code: 股票代码
    market: 市场标识 1=沪市, 0=深市
    klt: K线类型 101=日线, 102=周线, 103=月线……
    fqt: 复权方式 0=不复权, 1=前复权, 2=后复权
    begin/end: 时间区间戳, 不用可以默认
    """
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'secid': f'{market}.{stock_code}',
        'klt': klt,
        'fqt': fqt,
        'beg': begin,
        'end': end,
    }
    resp = requests.get(url, params=params)
    js = resp.json()
    klines = js['data']['klines']  # 每一项都是字符串，如 "2024-06-12,12.33,12.63,12.16,12.22,2286.91,0.08,0.66,1.14,12.22,12.33"

    # 自定义字段
    columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    df = pd.DataFrame([x.split(',') for x in klines], columns=columns)
    return df


if __name__ == "__main__":
    df = get_kline('300192', market='0')
    print(df.head())

    # 保存到csv
    df.to_csv("lesson02_kline.csv", index=False, encoding="utf-8-sig")
