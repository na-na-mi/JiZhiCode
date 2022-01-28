#先创建字典来容纳所有的站
Stations={1:"江北机场T2航站楼",
2:"碧津",
3:"双龙",
4:"回兴",
5:"长福路",
6:"翠云",
7:"园博园",
8:"鸳鸯",
9:"金童路",
10:"金渝",
11:"童家院子",
12:"龙头寺",
13:"重庆北站南广场",
14:"狮子坪",
15:"唐家院子",
16:"郑家院子",
17:"嘉州路",
18:"红旗河沟",
19:"观音桥",
20:"华新街",
21:"牛角沱",
22:"两路口",
23:"铜元局",
24:"工贸",
25:"南坪",
26:"四公里",
27:"重庆工商大学",
28:"六公里",
29:"重庆交通大学",
30:"八公里",
31:"麒龙",
32:"九公里",
33:"岔路口",
34:"花溪",
35:"大山村",
36:"学堂湾",
37:"鱼胡路",
38:"金竹",
39:"鱼洞"}
for i in Stations.keys():#遍历打印所有值
    print("第"+str(i)+"站"+":"+Stations[i] ) #str 将i强转化为str格式，这样防止报错，相当于连接字符串，结尾皆是如此。


#最关键的一步
NEWStations = {v:k for k,v in Stations.items()}#新字典，键值对互换  属于字典推导式，高阶技巧了属于是

#上车站查询
print("请输入上车站:")
s1 = input("")
for i in Stations.values():
    if s1 == i:
        print("查询成功，请问您在哪里下车？")
        break;
if  s1 not in Stations.values():
    print("没有找到该车站捏，请检查输入错误")
    
#下车站查询
s2 = input("")
for i in Stations.values():
    if s2 == i:
        print("完成啦！")
        break;
if  s2 not in Stations.values():
        print("没有找到该车站哦，请检查输入错误")
 

#车费计算环节
time = 2*NEWStations[s2] - 2*NEWStations[s1]#耗费时间 每站两分钟
if 0 < NEWStations[s2] - NEWStations[s1] <= 3:
    cost = 2
elif NEWStations[s2] - NEWStations[s1] <= 5:
    cost = 3
elif NEWStations[s2] - NEWStations[s1] <= 12:
    cost = NEWStations[s2] - 5 - NEWStations[s1] + 3
else:
     cost = 10
print("您所需费用为"+str(cost)+"元")
print("一共经过"+str(NEWStations[s2]-NEWStations[s1])+"站")
print("大约共需"+str(time)+"分钟")