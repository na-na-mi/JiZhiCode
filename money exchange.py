money = input("请输入带有单位的金额:\n ")
if money[0:3] in ['USD']:
    RMB = (eval(money[3:]))*6.78
    print("RMB{:.2f}".format(RMB))
elif money[0:3] in ['RMB']:
    USD = (eval(money[3:]))/6.78
    print("USD{:.2f}".format(USD))