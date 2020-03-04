# -*- coding: UTF-8 –*-
'''
哔哩哔哩爬虫，现可以进行搜索功能以及评论的爬取
作者：洪韬
时间：2020/3/4
'''
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from urllib.parse import quote
import json
import requests
import execjs
import time
import csv
import os
import re


class BiliBiliCrawl:
    def __init__(self):
        pass

    def __create_path(self, *path):
        finPath = ''
        for i in range(len(path)):
            finPath += path[i]
            if not os.path.exists(finPath):
                os.mkdir(finPath)
            finPath += '/'

    def __get_detail(self, html, write, isFirst=True):
        if isFirst:
            items = html('#all-list > div.flow-loader > div.mixin-list > ul>li').items()
        else:
            items = html('#all-list > div.flow-loader > ul>li').items()
        for item in items:
            itemDict = {
                'link': 'https:' + item('a').attr('href'),
                'title': item('div > div.headline.clearfix > a').text(),
                'watch': item('div > div.tags > span.so-icon.watch-num').text(),
                'bullet_chat': item('div > div.tags > span.so-icon.hide').text(),
                'time': item('div > div.tags > span.so-icon.time').text(),
                'up': item('div > div.tags > span:nth-child(4)').text()
            }
            write.writerow(itemDict)

    # 搜索，得到视频相关信息
    def search(self, keyword, path):
        self.__create_path(path, 'search')
        file = open(path + '/search/' + keyword + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['link', 'title', 'watch', 'bullet_chat', 'time', 'up']
        writer = csv.DictWriter(file, fieldnames)
        writer.writeheader()
        url = 'https://search.bilibili.com/all?keyword=' + quote(keyword) + '&from_source=nav_search_new'
        print('正在爬取第1页')
        rsp = requests.get(url)
        html = pq(rsp.text)
        self.__get_detail(html, writer)
        totalPages = eval(
            html('#all-list > div.flow-loader > div.page-wrap > div > ul > li.page-item.last').text().replace('\n',
                                                                                                              '').replace(
                ' ', ''))
        if totalPages == 1:
            print('爬取结束')
            return
        print('共有' + str(totalPages) + '页')
        for i in range(1, totalPages):
            time.sleep(1)
            print('正在爬取第' + str(i + 1) + '页')
            url = 'https://search.bilibili.com/all?keyword=' + quote(
                keyword) + '&from_source=nav_search_new&page=' + str(i + 1)
            rsp = requests.get(url)
            html = pq(rsp.text)
            self.__get_detail(html, writer, isFirst=False)
        print('爬取结束')
        file.close()

    # 得到某一个视频下的所有评论
    def get_comments(self, link,path):
        rsp=requests.get(link)
        html=pq(rsp.text)
        title=html('#viewbox_report > h1').text()
        self.__create_path(path,'comments')
        fieldnames=['name','sex','sign','content']
        file=open(path+'/comments/'+title+'.csv','w',encoding='utf-8',newline='')
        writer=csv.DictWriter(file,fieldnames=fieldnames)
        writer.writeheader()
        try:
            oid = re.compile('https://www.bilibili.com/video/av(.*?)spm_id_from').findall(link)[0].replace('?', '')
        except:
            oid=link.replace('https://www.bilibili.com/video/av','')
        se = execjs.eval('(new Date).getTime()')
        callback = execjs.eval('"jQuery" + ("1.7.2" + Math.random()).replace(/\D/g, "")')
        param = {
            'callback': callback,
            'jsonp': 'jsonp',
            'pn': '1',
            'type': '1',
            'oid': oid,
            'sort': '2',
            '_': str(int(time.time() * 1000))
        }
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'Sec-Fetch-Dest': 'script',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Referer': link,
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        count=1
        pages=-1
        while True:
            param['callback'] = callback+'_'+str(se)
            param['_'] = str(int(time.time() * 1000))
            param['pn']=str(count)
            print('正在爬取第'+str(count)+'页')
            url = 'https://api.bilibili.com/x/v2/reply?' + urlencode(param)
            rsp=requests.get(url,headers=headers)
            text=rsp.text.replace(param['callback']+'(','')[:-1]
            jsonText=json.loads(text)
            print(jsonText)
            if count==1:
                pages=int(jsonText['data']['page']['count']/jsonText['data']['page']['size'])+1
            if pages==count:
                break
            count+=1
            se += 1
            replies=jsonText['data']['replies']
            for reply in replies:
                itemDict={
                    'name':reply['member']['uname'].replace('\n','$'),
                    'sex':reply['member']['sex'].replace('\n','$'),
                    'sign':reply['member']['sign'].replace('\n','$'),
                    'content':reply['content']['message'].replace('\n','$')
                }
                writer.writerow(itemDict)
        file.close()
if __name__ == '__main__':
    app = BiliBiliCrawl()
    # 第一个参数为搜索的关键字，第二个参数为存储的位置
    # app.search('吃鸡', 'data')
    #爬取评论，第一个参数为视频链接，第二个参数为存储的位置
    app.get_comments('https://www.bilibili.com/video/av92463460','data')
