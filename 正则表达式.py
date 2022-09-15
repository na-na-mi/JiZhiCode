import requests


def gethtmltxt(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return "something error"


url = "http://www.baidu.com"
str = gethtmltxt(url)
