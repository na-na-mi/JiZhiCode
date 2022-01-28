import re
import requests as rq

def get_baidubaike():

    keyword = input('请输入你要查找的关键字:')
    url = 'http://baike.baidu.com/item/{}'.format(keyword)
    Header={
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
     }  
    html = rq.get(url , headers = Header).content.decode('utf-8')

    regex = re.compile('content="(.*?)">')
    words = re.findall(regex, html)[0]
    return words
  
if __name__ == '__main__':
    words = get_baidubaike()
    print(words)