import csv
import re
import requests
url='https://movie.douban.com/top250'
Header={
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
     }
resp=requests.get(url,headers=Header)
page_content=resp.text


obj=re.compile(r'</div>.*?<span class="title">(?P<名字>.*?)</span>.*?<p class="">'
                r'.*?<br>(?P<年份>.*?)&nbsp;.*?v:average">(?P<分数>.*?)</span>'
                r'.*?0"></span>.*?<span>(?P<人数>.*?)</span>.*?<span class="inq">'
                r'(?P<标语>.*?)</span>',re.S)

result=obj.finditer(page_content)
f=open("../data1.csv", mode="w", newline="") #newline去掉文件空行
csvwriter=csv.writer(f)
for it in result:
    print(it.group("名字"))
    print(it.group("年份").strip()) #去掉前面的空格和换行符
    print(it.group("分数"))
    print(it.group("人数"))
    print(it.group("标语"))
    dic=it.groupdict()
    dic['年份']=dic['年份'].strip()
    csvwriter.writerow(dic.values())
f.close()
resp.close()
print("over!")