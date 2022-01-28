import re
import requests
import bs4
url='https://movie.douban.com/top250'
Header={
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
     }
res=requests.get(url,headers=Header)
soup = bs4.BeautifulSoup(res.text,"html.parser")
targets = soup.find_all("div",class_="hd")
for each in targets:
	print(each.a.span.text)
