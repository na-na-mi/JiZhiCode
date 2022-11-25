# 本程序基于kaggle上的数据集，针对索尼，微软，任天堂三家游戏巨头进行具体分析并实行了力所能及范围内的可视化展示
# 采用线性回归方式进行分析，但是线性展示并不太直观，采用了大量饼图进行展示
# 最终结论得出本世代最受欢迎游戏机应当是索尼PS4（截止到2016，因为数据只到了这里，截止到目前为止，应当是索尼的PS5）
# 本世代最火热的游戏类型是 ACTION （动作），SHOOTING（射击）
import numpy as np  # 数据处理
import pandas as pd  # (e.g. pd.read_csv)
import seaborn as sns  # 基于matplotlib的高阶数据可视化展示库
from matplotlib import pyplot as plt  # 可视化展示
from brewer2mpl import qualitative  # 可以画出彩色的饼图
from tabulate import tabulate  # 统计数组，列表格之类的
import warnings

warnings.filterwarnings("ignore")
video = pd.read_csv(
    r'Video_Games_Sales_as_at_22_Dec_2016.csv')  # 定好文件路径，若无法打开请确保环境编码，文件编码都是UTF-8，在括号内加上encoding='utf-8'.
print(video.head())  # 检测是否读取成功
print(video.shape)
# 数据清洗过程，用线性回归方式清除不具备普遍性的离散点
video.isnull().any().any()  # 空行空列以NAN填上，统计各个属性的缺失值
# 后续计算各个属性的缺失值比例
video = video.dropna(axis=0)  # axis=0就是对横轴进行操作，为空的一组游戏数据就抛弃
tabulate(video.info(), headers='keys', tablefmt='psql')
print(video.Platform.unique())  # 对于一维数组或者列表，unique函数去除其中重复的元素，并按元素由大到小返回一个新的无元素重复的元组或者列表
str_list = []  # 空列表用来包含那些string
for colname, colvalue in video.iteritems():
    if type(colvalue[2]) == str:
        str_list.append(colname)
# 通过倒序排列得到数字列           
num_list = video.columns.difference(str_list)
# 创建只包含数字特征的数据图
video_num = video[num_list]
f, ax = plt.subplots(figsize=(14, 11))
plt.title('电子游戏数值特征与人群的相关性')
# 画一张热力图，像城市人口热力那种
# 该热力图可以显示任意两个数据集之间的相关性，颜色越深，相关性越强
sns.heatmap(video_num.astype(float).corr(), linewidths=0.25, vmax=1.0,
            square=True, cmap="cubehelix_r", linecolor='k', annot=True)

video7th = video[(video['Platform'] == 'Wii') | (video['Platform'] == 'PS3') | (video['Platform'] == 'X360')]
print(video7th.shape)
plt.style.use('dark_background')
yearlySales = video7th.groupby(['Year_of_Release', 'Platform']).Global_Sales.sum()
yearlySales.unstack().plot(kind='bar', stacked=True, colormap='PuBu',
                           grid=False, figsize=(13, 11))
plt.title('第7代游戏机（次世代）全球年销量的堆叠条形图')
plt.ylabel('Global Sales')
plt.style.use('dark_background')
ratingSales = video7th.groupby(['Rating', 'Platform']).Global_Sales.sum()
ratingSales.unstack().plot(kind='bar', stacked=True, colormap='Greens',
                           grid=False, figsize=(13, 11))
plt.title('第7代主机（次世代）每等级类型的销售堆叠条形图')
plt.ylabel('Sales')
plt.style.use('dark_background')
genreSales = video7th.groupby(['Genre', 'Platform']).Global_Sales.sum()
genreSales.unstack().plot(kind='bar', stacked=True, colormap='Reds',
                          grid=False, figsize=(13, 11))
plt.title('每种游戏类型的销售堆叠条形图')
plt.ylabel('Sales')
# 创造饼图
# 搞点颜色瞧瞧
plt.style.use('seaborn-white')
colors = ['#008DB8', '#00AAAA', '#00C69C']
plt.figure(figsize=(15, 11))
plt.subplot(121)
plt.pie(
    video7th.groupby('Platform').Global_Sales.sum(),
    # with the labels being platform
    labels=video7th.groupby('Platform').Global_Sales.sum().index,
    # with no shadows
    shadow=False,
    # stating our colors
    colors=colors,
    explode=(0.05, 0.05, 0.05),
    # with the start angle at 90%
    startangle=90,
    # with the percent listed as a fraction
    autopct='%1.1f%%'
)
plt.axis('equal')
plt.title('目前市场销量占有图')
plt.subplot(122)
plt.pie(
    video7th.groupby('Platform').User_Count.sum(),
    labels=video7th.groupby('Platform').User_Count.sum().index,
    shadow=False,
    colors=colors,
    explode=(0.05, 0.05, 0.05),
    startangle=90,
    autopct='%1.1f%%'
)
plt.axis('equal')
plt.title('占有用户的饼图')
plt.tight_layout()
video8th = video[(video['Platform'] == 'WiiU') | (video['Platform'] == 'PS4') | (video['Platform'] == 'XOne')]
video8th.shape
plt.style.use('dark_background')
genreSales = video8th.groupby(['Genre', 'Platform']).Global_Sales.sum()
genreSales.unstack().plot(kind='bar', stacked=True, colormap='Reds',
                          grid=False, figsize=(13, 11))
plt.title('每种游戏类型的销售堆叠条形图')
plt.ylabel('Sales')
plt.style.use('seaborn-white')
colors = ['#008DB8', '#00AAAA', '#00C69C']
plt.figure(figsize=(15, 11))
plt.subplot(121)
plt.pie(
    video8th.groupby('Platform').Global_Sales.sum(),
    # with the labels being platform
    labels=video8th.groupby('Platform').Global_Sales.sum().index,
    # with no shadows
    shadow=False,
    # stating our colors
    colors=colors,
    explode=(0.05, 0.05, 0.05),
    # with the start angle at 90%
    startangle=90,
    # with the percent listed as a fraction
    autopct='%1.1f%%'
)
plt.axis('equal')
plt.title('第八代（本世代）全球销售饼图')
plt.subplot(122)
plt.pie(
    video8th.groupby('Platform').User_Count.sum(),
    labels=video8th.groupby('Platform').User_Count.sum().index,
    shadow=False,
    colors=colors,
    explode=(0.05, 0.05, 0.05),
    startangle=90,
    autopct='%1.1f%%'
)
plt.axis('equal')
plt.title('第八代（本世代）游戏机全球用户分布')
plt.tight_layout()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示图里面的中文
plt.show()
