import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# 需要读取文件，程序才能成功运行
data = pd.read_csv(r"C:\Users\青山七海\OneDrive\桌面\data_temps1.csv", encoding='utf-8')

print("数据维度:", data.shape)  # 就是表格或者矩阵有几行几列
# print(data.describe())
# 获取年月日
years = data['year']
months = data['month']
days = data['day']

# datetime格式
dates = [str(int(year)) + '-' + str(int(month)) + '-' + str(int(day)) for year, month, day in zip(years, months, days)]
dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in dates]
# 开始绘图
plt.style.use('fivethirtyeight')
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))
fig.autofmt_xdate(rotation=35)
# 两天前最高气温的标签值
ax1.plot(dates, data['two days ago HT'])
ax1.set_xlabel('');
ax1.set_ylabel('Temperature');
ax1.set_title('two days ago Max Temp')
# 昨天的最高温度值
ax2.plot(dates, data['one day ago HT'])
ax2.set_xlabel('');
ax2.set_ylabel('Temperature');
ax2.set_title('Yesterday Max Temp')
# 今年平均的最高温度值
ax3.plot(dates, data['year average HT'])
ax3.set_xlabel('');
ax3.set_ylabel('Temperature');
ax3.set_title('year average Temp')
# 气象台预测
ax4.plot(dates, data['prediction'])
ax4.set_xlabel('');
ax4.set_ylabel('Temperature')
ax4.set_title('prediction')
plt.tight_layout(pad=2)
plt.show()

# 独热编码
features = pd.get_dummies(data)

labels = np.array(features['two days ago HT'])

# 在特征中去掉标签
features = features.drop('two days ago HT', axis=1)

# 名字单独保存一下，以备后患
feature_list = list(features.columns)

# 转换成合适的格式
features = np.array(features)

# 数据集切分


train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.25,
                                                                            random_state=42)

# 导入算法
from sklearn.ensemble import RandomForestRegressor

# 建模
rf = RandomForestRegressor(n_estimators=1000, random_state=42)

# 训练
rf.fit(train_features, train_labels)

# 预测结果
predictions = rf.predict(test_features)

# 计算误差
errors = abs(predictions - test_labels)

# mean absolute percentage error (MAPE)
mape = 100 * (errors / test_labels)

print('MAPE:', np.mean(mape))

# 导入所需工具包
from sklearn.tree import export_graphviz
import pydotplus  # pip install pydotplus

# 拿到其中的一棵树
tree = rf.estimators_[5]

# 导出成dot文件
export_graphviz(tree, out_file='tree.dot', feature_names=feature_list, rounded=True, precision=1)

# 绘图
(graph,) = pydotplus.graph_from_dot_file('tree.dot')

# 展示
graph.write_png('tree.png')

print('The depth of this tree is:', tree.tree_.max_depth)

# 限制一下树模型
rf_small = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
rf_small.fit(train_features, train_labels)

# 提取一颗树
tree_small = rf_small.estimators_[5]

# 保存
export_graphviz(tree_small, out_file='small_tree.dot', feature_names=feature_list, rounded=True, precision=1)

(graph,) = pydotplus.graph_from_dot_file('small_tree.dot')

graph.write_png('small_tree.png');

# 得到特征重要性
importances = list(rf.feature_importances_)

# 转换格式
feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]

# 排序
feature_importances = sorted(feature_importances, key=lambda x: x[1], reverse=True)

# 对应进行打印
[print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances]

# 选择最重要的那两个特征来试一试
rf_most_important = RandomForestRegressor(n_estimators=1000, random_state=42)

# 拿到这俩特征
important_indices = [feature_list.index('temp_1'), feature_list.index('average')]
train_important = train_features[:, important_indices]
test_important = test_features[:, important_indices]

# 重新训练模型
rf_most_important.fit(train_important, train_labels)

# 预测结果
predictions = rf_most_important.predict(test_important)

errors = abs(predictions - test_labels)

# 评估结果

mape = np.mean(100 * (errors / test_labels))

print('mape:', mape)

# 转换成list格式
x_values = list(range(len(importances)))

# 绘图
plt.bar(x_values, importances, orientation='vertical')

# x轴名字
plt.xticks(x_values, feature_list, rotation='vertical')

# 图名
plt.ylabel('Importance');
plt.xlabel('Variable');
plt.title('Variable Importances');

# 日期数据
months = features[:, feature_list.index('month')]
days = features[:, feature_list.index('day')]
years = features[:, feature_list.index('year')]

# 转换日期格式
dates = [str(int(year)) + '-' + str(int(month)) + '-' + str(int(day)) for year, month, day in zip(years, months, days)]
dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in dates]

# 创建一个表格来存日期和其对应的标签数值
true_data = pd.DataFrame(data={'date': dates, 'actual': labels})

# 同理，再创建一个来存日期和其对应的模型预测值
months = test_features[:, feature_list.index('month')]
days = test_features[:, feature_list.index('day')]
years = test_features[:, feature_list.index('year')]

test_dates = [str(int(year)) + '-' + str(int(month)) + '-' + str(int(day)) for year, month, day in
              zip(years, months, days)]

test_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in test_dates]

predictions_data = pd.DataFrame(data={'date': test_dates, 'prediction': predictions})

# 真实值
plt.plot(true_data['date'], true_data['actual'], 'b-', label='actual')

# 预测值
plt.plot(predictions_data['date'], predictions_data['prediction'], 'ro', label='prediction')
plt.xticks(rotation='60');
plt.legend()

# 图名
plt.xlabel('Date');
plt.ylabel('Maximum Temperature (F)');
plt.title('Actual and Predicted Values');
