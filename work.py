import re

str = '''<span class="td td-2nd"><a href="/air/nanchang.html" target="_blank">南昌市</a></span><span class="td 
td-4rd">17</span><span class="td td-4rd"><em class="f1" style="color:#79b800">优</em></span> '''
print(re.findall(r"\d\d", str))
print(re.findall(r"[6789]\d", str))
print(re.findall(r"td.", str))
s = 'aaa,bbb ccc high'
print(re.findall(r'[a-zA-Z]+', s))
print(re.findall(r"\d{2,}", str))
print(re.findall(r"\d{1,}b\d{1,}", str))
str2 = "fdfd<a>aaaaa</a>dfefe<b>bbbb</b>"
regex = '<.*?>.*?<\/.*?>'
print(re.findall(regex, str2))

str3 = "::ljz@yznu.edu.cn"
regex = '::([a-z]{2,13})@([a-z]{2,13})\.(com|edu|net|org|gov|yznu|)'
print(re.findall(regex, str3))

print(re.findall(r"td", str))
print(re.findall(r"^td", str))
a = "ipadress 192.168.31.5 bala"
regex2 = re.compile('((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
regex3 = re.compile('^ ((2((5[0 - 5]) | ([0 - 4]\d))) | ([0 - 1]?\d{1, 2}))(\.((2((5[0 - 5]) | ([0 - 4]\d))) | ([0 - 1]?\d{1, 2}))){3}$')
print(regex2.search(a))
print(regex3.search(a))
