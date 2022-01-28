#用python设计第一个游戏
temp = input("不妨猜一下阿鸡心里想的是哪个数字：")
guess = int(temp)

if guess == 8:
	print("你是阿鸡心里的蛔虫吗？！")
	print("哼！猜中了也没奖励！")
else:
	print("猜错啦，阿鸡心里想的是8！")
print("游戏结束，不玩啦！╰（‵□′）╯")
