import re
"""
This doc is using for study how to use regex in program.
Every different using way will be use with explain.

"""

# 限定符介绍
str_one = "ac abc aaabbcc abbbbbccc ababababc"
regex_one = 'ab?'  # ?前的字符是可有可无的。（仅一次）
regex_two = 'ab*'  # *前的字符可以没有，也可以出现多次。
regex_three = 'ab+c'  # +前的字符至少出现一次。
regex_four = 'ab{5}c'  # {}限定前字符出现次数，{5}为出现五次，{2，6}为出现二到六次，{2，}为出现六次以上
regex_five = '(ab){1,4}'  # 匹配连续字符

resultOne = re.findall(regex_one, str_one)
resultTwo = re.findall(regex_two, str_one)
resultThree = re.findall(regex_three, str_one)
resultFour = re.findall(regex_four, str_one)
resultFive = re.findall(regex_five, str_one)



if __name__ == '__main__':
    print(resultOne)
    print(resultTwo)
    print(resultThree)
    print(resultFour)
    print(resultFive)
