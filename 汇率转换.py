print("要兑换的钱的类型 美元（USD）人民币（RMB）")
a=(input("请输入：\n"))
b=input("请输入金额大小：\n")
if a==1:
    b=b*6
    print("结果是\n",b)
elif a==2:
    b=b/6
    print("结果是\n",b)
else:
    print("输入类型错误，重来")