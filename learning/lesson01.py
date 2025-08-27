import requests
import pandas as pd


# 爬虫东方财富股票接口


def get_stock_data(page=1, page_size=20):
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": page,
        "pz": page_size,
        "po": "1",  # 排序方式（1降序）
        "fs": "m:1+t:2",  # A股主板
        "fid": "f3",  # 涨跌幅排序
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f13"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    js = resp.json()
    print(js)

    # diff现在是一个dict而不是list
    # 将所有 value 转为 list
    data_list = list(js['data']['diff'].values())

    # 构造DataFrame
    df = pd.DataFrame(data_list)

    # 选择需要的字段
    select = ["f12", "f14", "f2", "f3", "f6"]
    df = df[select]
    df.columns = ["代码", "名称", "最新价", "涨跌幅(‰)", "成交额"]
    return df


if __name__ == "__main__":
    all_df = pd.DataFrame()
    for i in range(1, 3):  # 分页查询
        print(f"正在获取第{i}页...")
        df = get_stock_data(page=i, page_size=20)
        all_df = pd.concat([all_df, df], ignore_index=True)
    print(all_df)
    all_df.to_csv("lesson01_data.csv", index=False, encoding="utf-8-sig")