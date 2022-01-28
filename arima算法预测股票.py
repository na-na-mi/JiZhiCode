import matplotlib.pylab as plt
import pandas as pd
import datetime
from matplotlib.pylab import style
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from matplotlib.font_manager import FontProperties
from statsmodels.tsa.stattools import adfuller#adf检验平稳性
#去掉警告
import warnings
warnings.filterwarnings("ignore")

data1 = pd.read_csv(r"C:\Users\青山七海\Downloads\case003_基于ARIMA回归模型的股票价格预测_数据(1)\case003_基于ARIMA回归模型的股票价格预测_数据\data_stock1.csv", index_col = 0, parse_dates = [0], encoding = 'gbk')

data1_week = data1['收盘价'].resample('W-MON').mean()
print(data1_week)
#开始画图
data1_train = data1_week['2000':'2014'] 
plt.rcParams['font.sans-serif'] = ['SimHei'] #引用中文字体
#font1 = FontProperties(fname = r'C:\Windows\Fonts\simhei.ttf')
plt.figure(figsize=(8,2), dpi = 350)
data1_train.plot()
plt.title('股票收盘价')
plt.xlabel('时间')
plt.xlabel('股票收盘价')
plt.show()
adftest = adfuller(data1_train)
print(adftest[1])#[1]表示求出p，0.05以下表示平稳

#由于不平稳，需要做差分
data1_diff_1 = data1_train.diff()
print(data1_diff_1)#差分就是逐差法
data1_diff_2 = data1_diff_1.dropna()#第一项数据无效，舍弃
print(data1_diff_2)
#画图展示差分效果
plt.figure(figsize=(12,8),dpi = 350)
plt.plot(data1_diff_2)
plt.title('一阶差分效果')
plt.show()

adftest = adfuller(data1_diff_2)
print(adftest[1])


#绘制ACF图
plt.figure(dpi=350)
acf = plot_acf(data1_diff_2, lags = 20)
plt.title("ACF图")
plt.xlabel("阶数")
plt.ylabel("自相关系数")
plt.show()

#绘制PACF图
plt.figure(dpi = 350)
pacf = plot_pacf(data1_diff_2,lags = 20)
plt.title = ("PACF")
plt.xlabel("阶数")
plt.ylabel("偏自相关系数")
plt.show()

import statsmodels.api as sm
res = sm.tsa.arma_order_select_ic(data1_diff_2,max_ar = 5, max_ma = 5,ic = ['aic'])#限定AR,MA最大阶不超过5
print(res.aic_min_order)

#训练模型
model = ARIMA(data1_train, order = (1,1,1), freq ='W-MON')#用参数1，1，1建立模型
result_1 = model.fit()#训练模型

#预测股价
pred_1 = result_1.predict('20140609','20160627',dynaic = True, typ = 'levels' )
print(pred_1)

plt.figure(dpi = 600)
plt.xticks(rotation = 45)#将X轴的图例坐标值，倾斜45°放置
plt.plot(pred_1) #预测值
plt.plot(data1_week) # real
plt.show()
