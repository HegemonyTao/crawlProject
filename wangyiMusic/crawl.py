# -*- coding: UTF-8 –*-
'''
网易云音乐爬虫，现可以进行评论（热门评论以及全部评论）的爬取
作者：洪韬
时间：2020/3/11
'''
from Crypto.Cipher import AES
import base64
import requests
import json
import time
import csv
import os
import re



class wangyiCrawl:
    def __init__(self):
        self.Headers = {
            'Accept': "*/*",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Host': "music.163.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"

        }

        # 第二个参数
        self.second_param = "010001"
        # 第三个参数
        self.third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        # 第四个参数
        self.forth_param = "0CoJUm6Qyw8W8jud"

    def __create_path(self, *path):
        finPath = ''
        for i in range(len(path)):
            finPath += path[i]
            if not os.path.exists(finPath):
                os.mkdir(finPath)
            finPath += '/'

    def __get_params(self, page):
        # 获取encText，也就是params
        iv = "0102030405060708"
        first_key = self.forth_param
        second_key = 'F' * 16
        if page == 0:
            first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        else:
            offset = str((page - 1) * 20)
            first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (offset, 'false')
        self.encText = self.__AES_encrypt(first_param, first_key, iv)
        self.encText = self.__AES_encrypt(self.encText.decode('utf-8'), second_key, iv)
        return self.encText

    def __AES_encrypt(self, text, key, iv):
        # AES加密
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypt_text = encryptor.encrypt(text.encode('utf-8'))
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    # 获取热评以及全部评论
    def get_comments(self, url, path):
        rsp = requests.get(url.replace('#', ''), headers=self.Headers)
        title = re.compile('"title": "(.*?)",').findall(rsp.text)[0]
        self.__create_path(path, title)
        file1 = open(path + '/' + title + '/hotComments.csv', 'w', encoding='utf-8', newline='')
        file2 = open(path + '/' + title + '/comments.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['user', 'thumbs-up', 'time', 'comments']
        writer1 = csv.DictWriter(file1, fieldnames=fieldnames)
        writer1.writeheader()
        writer2 = csv.DictWriter(file2, fieldnames=fieldnames)
        writer2.writeheader()
        id = url.replace('https://music.163.com/#/song?id=', '')
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + id + '?csrf_token'
        params = self.__get_params(1)
        encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
        self.post = {
            'params': params,
            'encSecKey': encSecKey,
        }
        response = requests.post(url, headers=self.Headers, data=self.post)
        json_dict = json.loads(response.text)
        hotcomments = json_dict['hotComments']
        for i in hotcomments:
            time_local = time.localtime(int(i['time'] / 1000))  # 将毫秒级时间转换为日期
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            itemDict = {
                'user': i['user']['nickname'],
                'thumbs-up': str(i['likedCount']),
                'time': dt,
                'comments': i['content'].replace('\n', '')
            }
            writer1.writerow(itemDict)
        file1.close()
        comments_num = int(json_dict['total'])
        present_page = 0
        if (comments_num % 20 == 0):
            page = comments_num / 20
        else:
            page = int(comments_num / 20) + 1
        print("共有%d页评论" % page)
        # 逐页抓取
        for i in range(page):
            print('正在爬取第' + str(i + 1) + '页')
            params = self.__get_params(i + 1)
            encSecKey = encSecKey
            self.post = {
                'params': params,
                'encSecKey': encSecKey,
            }
            response = requests.post(url, headers=self.Headers, data=self.post)
            json_dict = json.loads(response.text)
            present_page = present_page + 1
            for i in json_dict['comments']:
                time_local = time.localtime(int(i['time'] / 1000))  # 将毫秒级时间转换为日期
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                itemDict = {
                    'user': i['user']['nickname'],
                    'thumbs-up': str(i['likedCount']),
                    'time': dt,
                    'comments': i['content'].replace('\n', '')
                }
                writer2.writerow(itemDict)
        file2.close()


if __name__ == '__main__':
    app = wangyiCrawl()
    #获取网易云音乐热门评论以及大概101页的评论
    app.get_comments('https://music.163.com/#/song?id=1429392929','data')
