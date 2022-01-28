import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


pd.set_option('display.max_columns', None)  
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.io as pio
import plotly.graph_objects as go
from plotly.offline import plot
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
df=pd.read_csv(r"C:\Users\青山七海\Downloads\archive (1)\Video_Games_Sales_as_at_22_Dec_2016.csv")#切换到自己文件的绝对路径，如果打开失败请加上encoding = 'utf-8'
print(df.head())
print(df.isnull().sum())
df = df[df["Year_of_Release"].notnull()]
df = df[df["Genre"].notnull()]
df = df[df["Publisher"].notnull()]
df['Year_of_Release']=df['Year_of_Release'].astype('int64')
df['User_Score']=df['User_Score'].replace('tbd',0).astype('float64')
sns.set_style("whitegrid")
trace1=go.Scatter(
                x=df.groupby(['Genre']).mean().reset_index()['Genre'], 
                y=df.groupby(['Genre']).mean().reset_index()['NA_Sales'],
                mode='lines+markers',
                name='North America Sales',
                marker = dict(size=8),
                line=dict(color = '#FA8072',width=2.5))
trace2=go.Scatter(
                x=df.groupby(['Genre']).mean().reset_index()['Genre'], 
                y=df.groupby(['Genre']).mean().reset_index()['EU_Sales'],
                mode='lines+markers',
                name='Europe Sales',
                marker = dict(size=8),
                line=dict(color = '#6495ED',width=2.5))
trace3=go.Scatter(
                x=df.groupby(['Genre']).mean().reset_index()['Genre'], 
                y=df.groupby(['Genre']).mean().reset_index()['JP_Sales'],
                mode='lines+markers',
                name='Japan Sales',
                marker = dict(size=8),
                line=dict(color = 'yellowgreen',width=2.5))

trace4=go.Scatter(
                x=df.groupby(['Genre']).mean().reset_index()['Genre'], 
                y=df.groupby(['Genre']).mean().reset_index()['Other_Sales'],
                mode='lines+markers',
                name='Other Country Sales',
                marker = dict(size=8),
                line=dict(color = '#DAA520',width=2.5))
edit_df=[trace1,trace2,trace3,trace4]
layout=dict(
            legend=dict(x=0.77, y=1.2, font=dict(size=10)), legend_orientation="v",
            title="Average Sales of Different Genre Games",
            xaxis=dict(title="Genre",tickfont=dict(size=8.35),zeroline=False,gridcolor="white"),
            yaxis=dict(title='Average Sales in Different Countries',gridcolor="#DCDCDC"),
            plot_bgcolor='white')


fig=dict(data=edit_df,layout=layout)
type(plot(fig))