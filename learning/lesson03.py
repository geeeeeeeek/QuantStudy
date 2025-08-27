import numpy as np
import pandas as pd

# numpy 教学

arr = np.array([1, 2, 3, 4, 5])
print(arr)

arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr)

arr = np.zeros((2, 3))
print(arr)

arr = np.ones((3, 2))
print(arr)

arr = np.arange(0, 10, 2)
print(arr)

# 数组的形状和类型
print(arr.dtype)
print(arr.shape)

# 数组的计算
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)
print(a * b)

# 切片
a = np.array([1,2,3,4,5])
print(a[0:2])

# 常用的函数

print(np.sum([10,11, 12]))
print(np.max([9, 8, 3]))

a = np.array([[1,2,3],[4, 5, 6]])
df = pd.DataFrame(a, columns=['name','sex','age'])
print(df)

# b = df.values
b = df.to_numpy()
print(b)

