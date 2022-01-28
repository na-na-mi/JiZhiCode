import random
import xlrd
file1 = xlrd.open_workbook(r'test.xlsx')
sheet1 = file1.sheet_by_name('Sheet')
i = []
x = input("请输入具体事件:")
y = int(input("老师要求的字数:"))
while len(str(i)) < y * 1.2:
    s = random.randint(1,60)
    rows = sheet1.row_values(s)
    i.append(*rows)
print("经历了近几个月的生活学习，我在思想上又发生了一些新的变化" + str(x) + "," *i)
print("这就是我这几个月的思想汇报总结。")
