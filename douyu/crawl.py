# -*- coding: UTF-8 –*-
'''
斗鱼爬虫：可以获取特定游戏的所有直播以及一个主播下的所有帖子
作者：洪韬
时间：2020/2/29
'''
from pyquery import PyQuery as pq
import requests
import random
import json
import csv
import re
import os


class DouYuCrawl:
    def __init__(self):
        self.__linkDict = {'lol云顶之弈': 'https://www.douyu.com/g_ydzhy', '绝地求生': 'https://www.douyu.com/g_jdqs',
                           'DOTA2': 'https://www.douyu.com/g_DOTA2', '英雄联盟': 'https://www.douyu.com/g_LOL',
                           '穿越火线': 'https://www.douyu.com/g_CF', 'DNF': 'https://www.douyu.com/g_DNF',
                           'CS:GO': 'https://www.douyu.com/g_CSGO', '暴雪游戏': 'https://www.douyu.com/g_blizzard',
                           '魔兽怀旧服': 'https://www.douyu.com/g_wowclassic', '炉石传说': 'https://www.douyu.com/g_How',
                           'COD16': 'https://www.douyu.com/g_COD', 'APEX英雄': 'https://www.douyu.com/g_APEX',
                           '自走棋': 'https://www.douyu.com/g_dota2rpg', '天涯明月刀': 'https://www.douyu.com/g_tianya',
                           'DOTA': 'https://www.douyu.com/g_DOTA', '魔兽世界': 'https://www.douyu.com/g_WOW',
                           '逆战': 'https://www.douyu.com/g_NZ', '魔兽争霸': 'https://www.douyu.com/g_mszb',
                           '主机游戏': 'https://www.douyu.com/g_TVgame', '逃离塔科夫': 'https://www.douyu.com/g_EFT',
                           '马里奥制造': 'https://www.douyu.com/g_Mario', '破坏领主': 'https://www.douyu.com/g_WLOM',
                           '恐怖游戏': 'https://www.douyu.com/g_Horror', '环世界': 'https://www.douyu.com/g_RimWorld',
                           '足球经理': 'https://www.douyu.com/g_Football', '怀旧游戏': 'https://www.douyu.com/g_classic',
                           '格斗游戏': 'https://www.douyu.com/g_FTG', '王者荣耀': 'https://www.douyu.com/g_wzry',
                           '和平精英': 'https://www.douyu.com/g_hpjy', '王者模拟战': 'https://www.douyu.com/g_wzrpg',
                           '热门手游': 'https://www.douyu.com/g_phone', '多多自走棋': 'https://www.douyu.com/g_zzq',
                           '梦幻西游三维版': 'https://www.douyu.com/g_MHXX3D', '百闻牌': 'https://www.douyu.com/g_BWP',
                           '棋牌娱乐': 'https://www.douyu.com/g_qipai', '火影忍者': 'https://www.douyu.com/g_hyrz',
                           '灌篮高手正版授权手游': 'https://www.douyu.com/g_glgs', 'CF手游': 'https://www.douyu.com/g_CFSY',
                           '跑跑手游': 'https://www.douyu.com/g_PPKDCSY', '新游中心': 'https://www.douyu.com/g_xyzx',
                           '猎人手游': 'https://www.douyu.com/g_lrlr', 'QQ飞车': 'https://www.douyu.com/g_qqfcsy',
                           '颜值': 'https://www.douyu.com/g_yz', '舞蹈': 'https://www.douyu.com/g_dance',
                           '二次元': 'https://www.douyu.com/g_ecy', '户外': 'https://www.douyu.com/g_HW',
                           '美食': 'https://www.douyu.com/g_ms', '互动交友': 'https://www.douyu.com/g_HDJY',
                           '乡野': 'https://www.douyu.com/g_xiangye', '一起看': 'https://www.douyu.com/g_yqk',
                           '数码科技': 'https://www.douyu.com/g_smkj', '在线教育': 'https://www.douyu.com/g_yj',
                           '科普': 'https://www.douyu.com/g_kepu', '直播中国': 'https://www.douyu.com/g_zjzg',
                           '汽车': 'https://www.douyu.com/g_car', '纪录片': 'https://www.douyu.com/g_jlp',
                           '达人': 'https://www.douyu.com/g_DR', '体育赛场': 'https://www.douyu.com/directory/sport/cate',
                           '交友': 'https://www.douyu.com/g_jiaoyou', '电台': 'https://www.douyu.com/g_DTAI',
                           '陪玩': 'https://www.douyu.com/g_PW', '正能量': 'https://www.douyu.com/g_znl',
                           '京斗云': 'https://www.douyu.com/g_jdy'}
        self.__headers = {
            'authority': 'www.douyu.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://www.douyu.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'dy_did=b8ca7e3c75732b4cfc393e9e00081501; acf_did=b8ca7e3c75732b4cfc393e9e00081501; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1582455222,1582455244,1582875977,1582885259; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1582886038'
        }

    def __get_links(self):
        url = "https://www.douyu.com/directory/all"
        response = requests.get(url, headers=self.__headers)
        compileText = re.compile('<div class="Aside-menu">(.*?)\n').findall(response.text)[0]
        allItems = re.compile('<div class="Aside-menu-list">(.*?)</div>').findall(compileText)
        linkDict = {}
        for item in allItems:
            html = pq(item)
            links = html('a').items()
            for link in links:
                linkDict[link.text()] = 'https://www.douyu.com' + link.attr('href')
        return linkDict

    def __safe_get(self, key, itemDict):
        try:
            return itemDict[key]
        except:
            return ''

    # 得到某一类型的全部直播间
    def get_info(self, liveType, path):
        if liveType not in self.__linkDict:
            print('不存在此类型')
            return
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/search'):
            os.mkdir(path + '/search')
        file = open(path + '/search/' + liveType + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['link', 'title', 'game', 'anchor', 'hot', 'tags']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        base_link = self.__linkDict[liveType]
        self.__headers['referer'] = 'https://www.douyu.com/directory/all'
        print('正在爬取第1页')
        rsp = requests.get(base_link, headers=self.__headers)
        html = pq(rsp.text)
        items = html('#listAll > div.layout-Module-container.layout-Cover.ListContent > ul>li').items()
        infos = re.compile('"list":(.*?)\n').findall(rsp.text)[0][:-1].replace('false', '"false"').replace('true',
                                                                                                           '"true"')
        tags = re.compile('"od":"(.*?)",').findall(infos)
        count = 0
        for item in items:
            itemDict = {
                'link': 'https://www.douyu.com' + item('div > a.DyListCover-wrap').attr('href'),
                'title': item('div > a.DyListCover-wrap > div.DyListCover-content > div:nth-child(1) > h3').text(),
                'game': item('div > a.DyListCover-wrap > div.DyListCover-content > div:nth-child(1) > span').text(),
                'anchor': item('div > a.DyListCover-wrap > div.DyListCover-content > div:nth-child(2) > h2').text(),
                'hot': item('div > a.DyListCover-wrap > div.DyListCover-content > div:nth-child(2) > span').text(),
                'tags': self.__safe_get(count, tags)
            }
            count += 1
            writer.writerow(itemDict)
        pages = eval(re.compile('"pageCount":(.*?),').findall(rsp.text)[0])
        if pages == 1:
            print('爬取结束')
            return
        print('共有' + str(pages) + '页')
        refererUrl = base_link
        id = re.compile('"tabTagPath":"/gapi/rkc/directory/c_tag/(.*?)/list",').findall(rsp.text)[0]
        for i in range(1, pages):
            print('正在爬取第' + str(i + 1) + '页')
            url = 'https://www.douyu.com/gapi/rkc/directory/' + id + '/' + str(i + 1)
            self.__headers['referer'] = refererUrl
            self.__headers['x-requested-with'] = 'XMLHttpRequest'
            rsp = requests.get(url, headers=self.__headers)
            jsonText = json.loads(rsp.text)
            datas = jsonText['data']['rl']
            for data in datas:
                hot = data['ol']
                if hot < 10000:
                    hot = str(hot)
                else:
                    hot = str(int(hot / 1000))
                    if hot[-1] == '0':
                        hot = hot[0] + '万'
                    else:
                        hot = hot[0] + '.' + hot[1] + '万'
                itemDict = {
                    'link': 'https://www.douyu.com/' + str(data['rid']),
                    'title': data['rn'],
                    'game': data['c2name'],
                    'anchor': data['nn'],
                    'hot': hot,
                    'tags': data['od']
                }
                writer.writerow(itemDict)
        file.close()

    # 得到一个主播下的所有帖子
    def get_post(self, link, path):
        id = link.replace('https://yuba.douyu.com/group/', '')
        headers = {
            'Host': 'yuba.douyu.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'sec-fetch-dest': 'empty',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': link,
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/post'):
            os.mkdir(path + '/post')
        url = 'https://yuba.douyu.com/wbapi/web/group/head?group_id=' + id + '&timestamp=' + str(random.random())
        rsp = requests.get(url, headers=headers)
        name = json.loads(rsp.text)['data']['group_name']
        file = open(path + '/post/' + name + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['link', 'name', 'title', 'describe', 'time', 'comments', 'imgUrls']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        print('正在爬取' + name + '的鱼吧')
        print('正在爬取第1页')
        url = 'https://yuba.douyu.com/wbapi/web/group/postlist?group_id=' + id + '&page=1&sort=1'
        rsp = requests.get(url, headers=headers)
        jsonText = json.loads(rsp.text)
        datas = jsonText['data']
        for data in datas:
            imgUrls = data['imglist']
            imgs = []
            for imgUrl in imgUrls:
                imgs.append(imgUrl['url'])
            itemDict = {
                'link': 'https://yuba.douyu.com/p/' + data['post_id'],
                'name': data['nickname'],
                'title': data['title'],
                'describe': data['describe'].replace('\n', ''),
                'time': data['last_reply_time'],
                'comments': data['comments'],
                'imgUrls': imgs
            }
            writer.writerow(itemDict)
        pages = int(jsonText['total'] / 30) + 1
        if pages == 1:
            print('爬取结束')
            return
        print('共有' + str(pages) + '页')
        for i in range(1, pages):
            print('正在爬取第' + str(i + 1) + '页')
            url = 'https://yuba.douyu.com/wbapi/web/group/postlist?group_id=' + id + '&page=' + str(i + 1) + '&sort=1'
            rsp = requests.get(url, headers=headers)
            jsonText = json.loads(rsp.text)
            datas = jsonText['data']
            for data in datas:
                imgUrls = data['imglist']
                imgs = []
                for imgUrl in imgUrls:
                    imgs.append(imgUrl['url'])
                itemDict = {
                    'link': 'https://yuba.douyu.com/p/' + data['post_id'],
                    'name': data['nickname'],
                    'title': data['title'],
                    'describe': data['describe'].replace('\n', ''),
                    'time': data['last_reply_time'],
                    'comments': data['comments'],
                    'imgUrls': imgs
                }
                writer.writerow(itemDict)
        file.close()


if __name__ == '__main__':
    app = DouYuCrawl()
    # 获取某游戏的全部直播，第一个参数是游戏名称，第二个参数是存储的位置
    # app.get_info('英雄联盟', 'data')
    # 获取主播下的所有帖子，第一个是链接，第二个是存储的位置
    #app.get_post('https://yuba.douyu.com/group/16775', 'data')
