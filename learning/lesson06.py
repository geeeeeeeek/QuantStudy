import pandas as pd

# pandas 教学

# 集合

s = pd.Series([1, 2, 3, 4, 5])
print(s)

# 表格
data = {
    'code': [111, 222, 333],
    'name': ['万科', '格力', '台积电']
}
df = pd.DataFrame(data)
print(df)

# 读取本地csv
df = pd.read_csv('test.csv')
print(df)

# 查看数据
print(df.head())
print(df.tail())
print(df.info())

# 选取数据
print(df['代码'])
print(df[['代码', '名称']])
print(df.iloc[0:2])
print(df.loc[0:2])

# 数据的筛选条件查询
print(df[df['最新价'] > 1000])
print(df[(df['最新价'] > 1000) & (df['代码'] == 600895)])

# 新建列/扩展列
df['interest'] = 1
print(df.head())

# 删除列
new_df = df.drop('成交额', axis=1)
print(new_df.head())

# 排序
new_df = df.sort_values('最新价', ascending=False)
print(new_df.head())

# 转换数据 -->numpy
# a = df.values
a = df.to_numpy()
print(a)