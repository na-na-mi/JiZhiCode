import requests
import csv
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  '(KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
}

movie_file = open('../豆瓣电影.csv', mode='a', newline='', encoding='utf8')
writer = csv.writer(movie_file)
writer.writerow(['电影名', '导演', '评分',  '评论', ])

# 列表解析，构建url列表
urls = ['https://movie.douban.com/top250?start={}'.format(i * 25) for i in range(10)]

# 创建空列表，用于存放数据
douban = []
movies = []

i = 0

for url in urls:
    res = requests.get(url, headers=headers)
    res.encoding = 'utf8'
    html = etree.HTML(res.text)
    tds = html.xpath('//tr[@class="item"]')

    for td in tds:
        # 获取书名
        book_name = td.xpath('.//a/@title')[0]
        # 获取作者
        author = td.xpath('.//p[@class=""]/text()')[0].split('/')[0]

        # 获取评分
        degree = td.xpath('.//p[@class="rating_nums"]/text()')[0]
        # 获取评论
        comments = td.xpath('.//span[@class="inq"]/text()')
        comment = comments[0] if len(comments) != 0 else '空'

        # 写入csv文件
        writer.writerow([book_name, author, degree, comment])

        book = {
            'name': book_name,
            'author': author,
            'degree': degree,
            'comment': comment
        }
        movies.append(book)

    douban.append(movies)

    i += 1
    print('第{}页爬取完毕'.format(i))

# 关闭文件
movie_file.close()
