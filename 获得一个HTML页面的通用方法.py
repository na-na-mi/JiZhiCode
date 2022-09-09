import requests
import re
def gethtmltxt(url):
  try:
    r = requests.get(url, timeout = 30)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text
  except:
    return "产生异常"
url = "http://www.baidu.com"
text = gethtmltxt(url)
print(text.title)