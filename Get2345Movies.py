import re
import requests
from bs4 import BeautifulSoup


def getHtml(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'gbk'
        return r.text
    except:
        return ''


def saveInfo(html):
    soup = BeautifulSoup(html, 'html.parser')
    move_ls = soup.find('ul', class_='hoverPopTarget clearfix')
    movies = move_ls.find_all('li')
    for top in movies:
        # 查找所有的图片链接
        img_url = top.find('img')['data-src']

        # 得到电影名称
        name = top.find('span', class_='title').get_text()

        # 上映时间
        t = top.find('a', class_='v_picTxt')['data-ajax25tab']
        try:
            time = re.findall('\d\d\d\d', t)[0]
        except:
            time = '暂时无上映时间信息'

        # 评分
        try:
            score = top.find('span', class_='rate').get_text()
        except:
            score = '暂时无评分'

        # 演员表
        try:
            actors = top.find('p', class_='pActor')
            actor = ''
            for act in actors.contents:
                actor = actor + act.string + ' '
        except:
            actor = '暂时无演员姓名'
        # 简介
        if top.find('p', class_='pTxt pIntroHide'):
            intro = top.find('p', class_='sub-tit').get_text()
        else:
            intro = top.find('p', class_='sub-tit').get_text()
        print('影片名：{}  上映年份{}\n演员{}\n简介{}\n{}\n'.format(name, time, actor, intro, score))


def main():
    url = 'https://dianying.2345.com'
    html = getHtml(url)
    saveInfo(html)


main()
