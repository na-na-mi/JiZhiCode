#用python设计第一个guess number游戏
from random import * #导入随机数模块
answer = randint(1, 50)
counts = 5
print("这是一个猜数字的游戏，数字应当在1——50之间\n")
while counts > 0:

        temp = input("不妨猜一下我心里想的是哪个数字：")
        guess = int(temp)

        if guess == answer:
                print("你是俺心里的蛔虫吗？！")
                print("哼！猜中了也没奖励！")
                break #强制跳出循环
        else:
                if guess > answer: #套娃
                        print("大了")
                else:
                        print("小啦！")
          
        counts = counts - 1
        print("还有{}次机会".format(counts))
print("游戏结束，不玩啦！╰（‵□′）╯")

