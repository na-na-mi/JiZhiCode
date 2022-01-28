import numpy as np
import matplotlib.pyplot as plt
t = np.arange(1,10,1)#创建时间轴
print(t)
y = 0.9*t + np.sin(t)#拟合函数，根据现有的值去猜出来
print(y)#纵轴数值
plt.plot(t,y,"o")#画出现有点
model = np.polyfit(t,y,deg = 1)#创建一阶函数模型
t2 = np.arange(-2,12,0.1)
y2predict = np.polyval(model,t2)#预测值
plt.plot(t,y,'o',t2,y2predict,'x')#绘制出预测曲线
plt.show()#画出来
