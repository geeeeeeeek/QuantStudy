import numpy as np
import pandas as pd

# numpy 教学

# 数组
a = np.array([1, 2, 3, 4, 5])
print(a)
# 二组数组
b = np.array([[1, 2, 3],[4, 5, 6]])
print(b)
# 0 1
zeros = np.zeros((2, 3))
print(zeros)
ones = np.ones((3, 2))
print(ones)
# 指定范围
arr = np.arange(1, 10, 2)
print(arr)
# 查看数组特征
print(b.shape)
print(b.dtype)
# 数组的运算
a = np.array([1, 2, 3])
b = np.array([3, 4, 5])
print(a + b)
print(a * b)
# 切片
a = np.array([1, 2, 3, 4, 5])
print(a[1:3])
b = np.array([[1, 2, 3],[4, 5, 6]])
print(b[1, 0])
print(b[:, 1])
# 常用的函数
print(np.sum(a))
print(np.mean(a))
print(np.max(a))
# 数据类型 pandas
# 从numpy转pandas
arr = np.array([[1, 2, 3],[4, 5, 6]])
df = pd.DataFrame(arr)
print(df)
# 从pandas转numpy
data = {'A':[1, 2, 3], 'B':[4, 5, 6]}
df = pd.DataFrame(data)
print(df)

# arr = df.values
arr = df.to_numpy()
print(arr)
