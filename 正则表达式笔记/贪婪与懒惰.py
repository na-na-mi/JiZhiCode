import re

"""
This doc is using for study how to use regex in program.
Every different using way will be use with explain.

"""

# 限定符介绍
str_one = '''<span class="td td-2nd"><a href="/air/nanchang.html" target="_blank">南昌市</a></span><span class="td 
td-4rd">17</span><span class="td td-4rd"><em class="f1" style="color:#79b800">优</em></span>'''
regex_one = '<.+?>'  # 懒惰模式
regex_two = '<.+>'  # 贪婪模式

resultOne = re.findall(regex_one, str_one)
resultTwo = re.findall(regex_two, str_one)

if __name__ == '__main__':
    print(resultOne)
    print(resultTwo)
