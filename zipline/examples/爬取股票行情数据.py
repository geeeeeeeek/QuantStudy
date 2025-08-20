import requests
import pandas as pd

"""
爬取股票行情脚本
"""

# 股票代码
stock = "s_sh511970,s_sh511980"
r = requests.get("http://hq.sinajs.cn/list=" + stock)

if r.status_code == 200:
    print(r.text)
    stock_list = []
    split_lines = r.text.splitlines()

    for line in split_lines:
        # var hq_str_s_sh511980="现金添富,99.998,0.009,0.01,152,153";
        stock_id = line[line.find("=") - 8: line.find("=")]
        right_str = line[line.find("\"") + 1: line.rindex("\"")]
        if len(right_str) > 0:
            stock_field_list = right_str.split(",")
            stock_field_list[1] = round(float(stock_field_list[1]), 2)
            if stock_field_list[1] > 0:
                stock_field_list.append(stock_id)
                stock_list.append(stock_field_list)
    print(stock_list)

    df = pd.DataFrame(stock_list, columns=['名称', '价格', '涨跌额',
                                           '涨跌幅', '成交量', '成交额',
                                           '股票代码'])

    df.to_csv('out.csv', index=False)
