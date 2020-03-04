# -*- coding: UTF-8 –*-
'''
抖音爬虫，现可以进行个人信息的爬取
作者：洪韬
时间：2020/3/2
'''
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from docx.shared import Inches
from docx import Document
import requests
import re
import os


class DouYinCrawl:
    def __init__(self):
        self.__transDict = {'xe602': '1', 'xe603': '0', 'xe604': '3', 'xe605': '2', 'xe606': '4', 'xe607': '5',
                            'xe608': '6',
                            'xe609': '9', 'xe60a': '7', 'xe60b': '8', 'xe60c': '4', 'xe60d': '0', 'xe60e': '1',
                            'xe60f': '5',
                            'xe610': '2', 'xe611': '3', 'xe612': '6', 'xe613': '7', 'xe614': '8', 'xe615': '9',
                            'xe616': '0',
                            'xe617': '2', 'xe618': '1', 'xe619': '4', 'xe61a': '3', 'xe61b': '5', 'xe61c': '7',
                            'xe61d': '8',
                            'xe61e': '9', 'xe61f': '6'}
        self.__headers = {
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'sec-fetch-dest': 'document',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '_ga=GA1.2.913540324.1582983429; _gid=GA1.2.1576801560.1582983429;'
        }

    def __safe_get(self, key, itemDict):
        try:
            return itemDict[key]
        except:
            return ''

    def __create_path(self, *path):
        finPath = ''
        for i in range(len(path)):
            finPath += path[i]
            if not os.path.exists(finPath):
                os.mkdir(finPath)
            finPath += '/'

    def __trans(self, transStr):
        finStr = transStr
        finStr = finStr.replace('&#', '').replace(';', '')
        for key in self.__transDict:
            finStr = finStr.replace(key, self.__transDict[key])
        return finStr

    def __add_param(self, document, boldWord, num):
        p = document.add_paragraph()
        p.add_run(boldWord).bold = True
        p.add_run(':' + num)

    # 得到某一个抖音号的信息
    def get_info(self, link, path):
        response = requests.get(link, headers=self.__headers)
        html = pq(response.text)
        imgUrl = html('#pagelet-user-info > div.personal-card > div.info1 > span.author > img').attr('src')
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
        tempRsp = requests.get(imgUrl, headers=headers)
        name = html('#pagelet-user-info > div.personal-card > div.info1 > p.nickname').text()
        self.__create_path(path, name)
        file = open(path + '/' + name + '/temp.png', 'wb')
        file.write(tempRsp.content)
        file.close()
        info = html('#pagelet-user-info > div.personal-card > div.info2 > div > span').text()
        signature = html('#pagelet-user-info > div.personal-card > div.info2 > p.signature').text()
        id = self.__trans(re.compile('<p class="shortid">(.*?)</p>').findall(response.text)[0])
        focus = self.__trans(re.compile('<span class="num">(.*?)</span>').findall(response.text)[0])
        follow = self.__trans(
            re.compile('<span class="follower block"><span class="num">(.*?)</span> </span>').findall(response.text)[0])
        liked = self.__trans(
            re.compile('<span class="liked-num block"><span class="num">(.*?)</span>').findall(response.text)[0])
        production = self.__trans(
            re.compile('<div class="user-tab active tab get-list" data-type="post">(.*?)</div>').findall(response.text)[
                0])
        like = self.__trans(
            re.compile('<div class="like-tab tab get-list" data-type="like">(.*?)</div>').findall(response.text)[0])
        id = pq(id).text().replace(' ', '').replace('抖音ID：', '')
        focus = pq(focus).text().replace(' ', '')
        follow = pq(follow).text().replace(' ', '').replace('粉丝', '')
        liked = pq(liked).text().replace(' ', '')
        production = pq(production).text().replace(' ', '').replace('作品', '')
        like = pq(like).text().replace(' ', '').replace('喜欢', '')
        document = Document()
        document.add_heading(name, 0)
        document.add_picture(path + '/' + name + '/temp.png', width=Inches(1.25))
        self.__add_param(document, '抖音ID', id)
        document.add_paragraph(info)
        document.add_paragraph(signature)
        self.__add_param(document, '关注', focus)
        self.__add_param(document, '粉丝', follow)
        self.__add_param(document, '赞', liked)
        self.__add_param(document, '作品', production)
        self.__add_param(document, '喜欢', like)
        document.save(path + '/' + name + '/info.docx')
        os.remove(path + '/' + name + '/temp.png')

    # 不可用
    # 得到某个抖音号下的所有视频
    def get_videos(self, link):
        session = requests.Session()
        rsp = session.get(link, headers=self.__headers)
        tac = re.compile('<script>tac=(.*?)</script>').findall(rsp.text)[0]
        param = {
            'sec_uid': 'MS4wLjABAAAAAEtO1dCIZvj4VWbLU4Xce7DgVgsKNMNu88eNR2c2LtY',
            'count': '21',
            'max_cursor': '0',
            'aid': '1128',
            '_signature': 'uiHDTxAU5IhS--EyZo.-vrohw1',
            'dytk': '2a1b5dd877dee2ad7b3fe40c26b778c4'
        }
        sec_uid = self.__safe_get(0, re.compile('sec_uid=(.*?)&').findall(rsp.url))
        param['sec_uid'] = sec_uid
        user_id = re.compile('uid: "(.*?)",').findall(rsp.text)[0]
        _signature = 'none'
        if sec_uid == '':
            param['user_id'] = user_id
        dytk = re.compile("dytk: '(.*?)'\n").findall(rsp.text)[0]
        param['dytk'] = dytk
        param['_signature'] = _signature
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?' + urlencode(param)
        headers = {
            'authority': 'www.iesdouyin.com',
            'accept': 'application/json',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': rsp.url,
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '_ga=GA1.2.1890981537.1583055242; _gid=GA1.2.1273232001.1583055242; tt_webid=6799172811283072525; _ba=BA0.2-20200229-5199e-9KN349EE8pluQufNXg9O'
        }
        print(url)
        rsp = session.get(url, headers=headers)
        print(rsp.text)


if __name__ == '__main__':
    app = DouYinCrawl()
    #第一个参数为个人信息链接，第二个参数为存储的位置
    # app.get_info('https://v.douyin.com/tSnqbr/', 'data')
