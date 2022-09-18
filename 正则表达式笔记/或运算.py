import re

"""
This doc is using for study how to use regex in program.
Every different using way will be use with explain.

"""

# 或运算介绍
str_one = "a cat a dog a bird an apple"

regex_one = 'a (cat|dog)'  # 仅匹配 cat or dog
regex_two = 'a cat|dog'  # 匹配 a cat    or   dog

resultOne = re.findall(regex_one, str_one)
resultTwo = re.findall(regex_two, str_one)

if __name__ == '__main__':
    print(resultOne)
    print(resultTwo)
