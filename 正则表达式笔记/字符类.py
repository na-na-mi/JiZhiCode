import re

"""
This doc is using for study how to use regex in program.
Every different using way will be use with explain.

"""

# 或运算介绍
str_one = "abc tiger lion aabbcc ljz400216@163.com 876873131"

regex_one = '[abc]+'  # 方括号表示匹配的字符只能取自它们
regex_two = '[a-z]'  # 匹配 所有的小写字符。大写 数字类同理
regex_three = '[^a-z]+'  # 匹配非小写字符 包括空格换行回车

resultOne = re.findall(regex_one, str_one)
resultTwo = re.findall(regex_two, str_one)
resultThree = re.findall(regex_three, str_one)

if __name__ == '__main__':
    print(resultOne)
    print(resultTwo)
    print(resultThree)
