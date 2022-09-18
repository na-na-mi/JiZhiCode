import re

"""
This doc is using for study how to use regex in program.
Every different using way will be use with explain.

"""

# 元字符介绍  大写与小写所匹配内容相反
str_one = "abc" \
          " tiger" \
          " lion" \
          " aabbcc" \
          " ljz400216@163.com" \
          " 876873131" \
          " 761_911"
regex_one = '\d'  # 匹配数字
regex_two = '\w'  # 匹配单词，单词数字下划线
regex_three = '\s'  # 空白符，换行符
regex_four = '\b'  # 表示单词字符的边界
regex_five = '.'  # 一个点表示任意字符，除了换行符。
regex_six = '^a'  # 匹配行首
regex_seven = 'c$'  # 匹配行尾
resultOne = re.findall(regex_one, str_one)
resultTwo = re.findall(regex_two, str_one)
resultThree = re.findall(regex_three, str_one)
resultFour = re.findall(regex_four, str_one)
resultFive = re.findall(regex_five, str_one)
resultSix = re.findall(regex_six, str_one)
resultSeven = re.findall(regex_seven, str_one)

if __name__ == '__main__':
    print(resultOne)
    print(resultTwo)
    print(resultThree)
    print(resultFour)
    print(resultFive)
    print(resultSix)
    print(resultSeven)
