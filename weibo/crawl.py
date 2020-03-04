# -*- coding: UTF-8 –*-
'''
微博搜索爬虫：暂时只可以实现搜索功能
作者：洪韬
时间：2020/2/27
'''
from pyquery import PyQuery as pq
from urllib.parse import quote
import requests
import login
import csv
import os

session = requests.Session()


class WeiBoCrawl:
    def __init__(self, s):
        self.session = s
        self.__headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Referer': 'https://weibo.com/u/6673533934/home?wvr=5&lf=reg',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    def search(self, keyword, path):
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/search'):
            os.mkdir(path + '/search')
        file = open(path + '/search/' + keyword + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['author', 'authorLink', 'content', 'forward', 'forward', 'comments', 'fabulous', 'time', 'source']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        refererUrl = ''
        for i in range(50):
            print('正在爬取第' + str(i + 1) + '页')
            if i == 0:
                url = "https://s.weibo.com/weibo/" + quote(quote(keyword)) + "?topnav=1&wvr=6"
                print(url)
                response = self.session.get(url, headers=self.__headers)
                refererUrl = response.url
            else:
                self.__headers['Referer'] = refererUrl
                url = "https://s.weibo.com/weibo/" + quote(quote(keyword)) + "?topnav=1&wvr=6&b=1&page=" + str(i + 1)
                print(url)
                refererUrl = url
                response = self.session.get(url, headers=self.__headers)
            html = pq(response.text)
            allItems = html('#pl_feedlist_index > div:nth-child(1) > div[action-type=feed_list_item]').items()
            for item in allItems:
                content = item('div.content > p:nth-child(3)').text()
                if content == '':
                    content = item('div.content > p:nth-child(2)').text()
                else:
                    content = content.replace('收起全文d', '')
                content = content.replace('\n', '')
                itemDict = {
                    'author': item('div.content > div.info > div:nth-child(2) > a.name').text(),
                    'authorLink': 'https:' + item('div.content > div.info > div:nth-child(2) > a.name').attr('href'),
                    'content': content,
                    'forward': item('div.card-act > ul > li:nth-child(2) > a').text().replace('转发', ''),
                    'comments': item('div.card-act > ul > li:nth-child(3) > a').text().replace('评论', ''),
                    'fabulous': item('div.card-act > ul > li:nth-child(4) > a').text(),
                    'time': item('div.content > p.from > a:nth-child(1)').text(),
                    'source': item('div.content > p.from > a:nth-child(2)').text()
                }
                print(itemDict)
                writer.writerow(itemDict)
        file.close()


if __name__ == '__main__':
    s = requests.Session()
    weib = login.Weibo('18297420903', 'GFD1314ngu', s)
    weib.main()
    app = WeiBoCrawl(s)
    # 搜索：第一个参数为关键字，第二个参数为存储的路径，共爬取50页
    app.search('复学', 'data')
