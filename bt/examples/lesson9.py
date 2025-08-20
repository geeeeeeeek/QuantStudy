import numpy as np
import pandas as pd

data = pd.read_csv("../csv/data_eth.csv")

print(data[0: 2])
up = np.max(data["high"].iloc[-20:])
down = np.min(data["low"].iloc[-int(20 / 2):])
# print(up)
# print(down)
# print(data["high"].iloc[-1])
# print(data.high.iloc[-1])

def in_or_out(data, price, T=20):
    up = np.max(data["high"].iloc[-T:])
    down = np.min(data["low"].iloc[-int(T / 2):])
    print("当前价格为: %s, 唐奇安上轨为: %s, 唐奇安下轨为: %s" % (price, up, down))
    if price > up:
        print("价格突破唐奇安上轨")
        return 1
    elif price < down:
        print("价格跌破唐奇安下轨")
        return -1
    else:
        return 0

# ATR值计算
def calc_atr(data):
    tr_list = []
    for i in range(1, len(data)):
        tr = max(data["high"].iloc[i] - data["low"].iloc[i],
                 abs(data["high"].iloc[i] - data["close"].iloc[i - 1]),
                 abs(data["close"].iloc[i - 1] - data["low"].iloc[i]))
        tr_list.append(tr)
    atr = np.array(tr_list).mean()
    return atr

def calc_size(value, price):
    return value * 0.1 / price

print(in_or_out(data, 2169, 20))
print(calc_atr(data[-14:]))
print(calc_size(1000, 10.5))