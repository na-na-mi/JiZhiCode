import jieba
txt = open(r"D:\红楼梦.txt","r",encoding='utf-8').read()
words = jieba.lcut(txt)  
counts = {}  
excludes = ['什么','一个','我们','那里','如今','你们','说道','知道','起来','姑娘','这里','出来',
            '他们','众人','奶奶','自己','一面','只见','怎么','两个','没有','不是','不知','听见',
            '这个','这样','进来','咱们','就是','东西','告诉','回来','只是','大家','只得','这些',
            '不敢','出去','所以','不过','不好','的话','一时','过来','不能','心里','今日','姐姐',
            '太太','丫头','银子','如此','二人','几个','答应','这么','还有','只管','一回','说话',
            '那边','外头','这话','打发','自然','罢了','今儿','屋里']
for word in words:
    if len(word) == 1:
        continue
    else :
        counts[word] = counts.get(word,0) + 1  
for word in excludes:
    del counts[word]  
items = list(counts.items()) 
items.sort(key = lambda x:x[1],reverse=True)  
for i in range(20):
    word, count = items[i]
print("{0:<10}{1:>5}".format(word, count))
