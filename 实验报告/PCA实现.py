from _winapi import NULL
import numpy as np
import pandas as pd

data = pd.read_csv("PCAdata.csv", index_col=["地区"])
print(data)
data_Decentralized = pd.DataFrame(index=data.index, columns=data.columns, dtype=np.float32)  # 中心化定义的数据，初始值为空
data_COV = NULL  # 协方差结果数据
# 计算均值
data_average = data.mean()

for row in data:
    for col in data.index:
        data_Decentralized[row][col] = data[row][col] - data_average[row]

data_COV = np.cov(data_Decentralized, rowvar=False)

eigenValue, eigenVectors = np.linalg.eig(data_COV)

for i in range(len(eigenValue)):
    for j in range(len(eigenValue) - 1):
        if eigenValue[j + 1] < eigenValue[j]:
            tempVectors = eigenVectors[j + 1].copy()
            eigenVectors[j + 1] = eigenVectors[j].copy()
            eigenVectors[j] = tempVectors

            temp = eigenValue[j + 1]
            eigenValue[j + 1] = eigenValue[j]
            eigenValue[j] = temp

finalData = data_Decentralized.values.dot(eigenVectors[0:2].T)
# 降维后的数据和维度
print(finalData, finalData.shape)
