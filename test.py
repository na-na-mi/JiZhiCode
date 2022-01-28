'''#判断回文数
s = input("请输入一个数")
s = str(s)
n = s[::-1]
if s==n:
    print("true")
else:
    print("False")'''
'''import random
 
def rea(n):
    count = 0
    for i in range(n):
        a = random.randint(1,6) + random.randint(1,6)
        if a==10:
            count+=1
    return count / n
 
print(rea(1000))
print(rea(10000))
print(rea(100000))'''

'''list = []
for sun in range(2000,2200):
    if sun%7==0:
        if sun%5!=0:
            list.append(sun)
print(list)'''
'''slist=[]
x,y = map(lambda x:int(x),input("请输入两个数：").split(','))
for i in range(x):
    temp=[]
    for j in range(y):
        temp.append(i*j)
    list.append(temp)
print(list)'''

str=input()
list=str.split(',')
flag=True
for i in list:
    temp=int(i,2)
    if temp%5==0:
        if flag:
            print(i,end='')
            flag=False
        else:
            print(",{}".format(i))
