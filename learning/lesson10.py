import matplotlib.pyplot as plt
import pandas as pd

# matplotlib数据可视化库


# 折线图/散点图/饼图/柱状图

plt.plot([1, 2, 3, 4, 5, 6, 7, 8, 9], [20, 17, 22, 20, 29, 39, 18, 20, 40])
plt.scatter([1, 2, 3, 4], [10, 20, 12, 18])
plt.pie([30, 50, 20], labels=['A', 'B', 'C'])
plt.bar(['A', 'B', 'C'], [20, 25, 10], color='blue')

# 图表的美化
plt.title("test")
plt.xlabel("XXXX")
plt.ylabel("YYYY")
plt.grid()

# 保存图片
# plt.savefig("aaa.png")

# 多图显示
# plt.subplot(1, 2, 1)
# plt.plot([1, 2, 3], [4, 5, 3])
# plt.subplot(1, 2, 2)
# plt.bar(['A', 'B', 'C'], [100, 200, 140])

# 与pandas的结合
# df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
# plt.plot(df['x'], df['y'])

# 读取本地csv数据并绘制
# df = pd.read_csv("test2.csv")
# plt.plot(df['datetime'], df['close'])
# plt.xticks(rotation=45)

plt.show()
