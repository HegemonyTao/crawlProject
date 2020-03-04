# -*- coding: UTF-8 –*-
'''
淘宝爬虫，现可以进行搜索，根据链接爬取评论
作者：洪韬
时间：2020/2/24
'''
from urllib.parse import urlencode
from pyquery import PyQuery as pq
import requests
import random
import time
import csv
import json
import re
import os

s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class TaoBaoLogin:

    def __init__(self, session):
        """
        账号登录对象
        :param username: 用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码
        """
        # 检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        # 验证淘宝用户名密码URL
        self.verify_password_url = "https://login.taobao.com/member/login.jhtml"
        # 访问st码URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘宝个人 主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘宝用户名
        self.username = '18297420903'
        # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
        self.ua = '122#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'
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.TPL_password2 = '50e9cfe9c42c3994370b30f90e3bfd22e1d7724cbde7ceb2eda53e41e50c8b144636217a146f7c5d002da97bfb3b47a11942bdbc465ae08d7f4e9861af288eeafe996baf114182254b769417b280f033b194303c72691a4dfbc3c427e2ae148c5b48458ad9c2cda86e10df8098ae460c9dd02d3f9fe693c3604979d7be86cd56'

        # 请求超时时间
        self.timeout = 3
        # session对象，用于共享cookies
        self.session = session

        if not self.username:
            raise RuntimeError('请填写你的淘宝用户名')

    def _user_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'username': self.username,
            'ua': self.ua
        }
        try:
            response = self.session.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _verify_password(self):
        """
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        """
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm',
        }
        # 登录toabao.com提交的数据，如果登录失败，可以从浏览器复制你的form data
        verify_password_data = {
            'TPL_username': self.username,
            'ncoToken': '78401cd0eb1602fc1bbf9b423a57e91953e735a5',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            # 'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61323330722E312E3735343839343433372E372E33353836363032633279704A767526663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246732E74616F62616F2E636F6D25324673656172636825334671253344253235453925323538302532353946253235453525323542412532354136253235453925323538302532353946253235453525323542412532354136253236696D6766696C65253344253236636F6D6D656E64253344616C6C2532367373696425334473352D652532367365617263685F747970652533446974656D253236736F75726365496425334474622E696E64657825323673706D253344613231626F2E323031372E3230313835362D74616F62616F2D6974656D2E31253236696525334475746638253236696E69746961746976655F69642533447462696E6465787A5F3230313730333036',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1440*900',
            'osVer': 'macos|10.145',
            'naviVer': 'chrome|76.038091',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'osPF': 'MacIntel',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'TD0789BC99BFBBF893B3C8C0E1729CCA3CB0469EA11FF6D196BA826C8EB',
            'ua': self.ua
        }
        try:
            response = self.session.post(self.verify_password_url, headers=verify_password_headers,
                                         data=verify_password_data,
                                         timeout=self.timeout)
            response.raise_for_status()
            # 从返回的页面中提取申请st码地址
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        # 提取申请st码url
        apply_st_url_match = re.search(r'<script src="(.*?)"></script>', response.text)
        # 存在则返回
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        """
        申请st码
        :return: st码
        """
        apply_st_url = self._verify_password()
        try:
            response = self.session.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True
        # 判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e
        # 登录成功，提取跳转淘宝用户主页url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        self.session.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝登录cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return: 淘宝昵称
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))


class TaoBao:
    def __init__(self):
        self.__headers = {
            'authority': 's.taobao.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://www.taobao.com/?spm=a1z02.1.1581860521.1.1def782dKVefPo',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        self.__param = {
            'q': 'keyword',
            'imgfile': '',
            'commend': 'all',
            'ssid': 's5-e',
            'search_type': 'item',
            'sourceId': 'tb.index',
            'spm': 'a21bo.2017.201856-taobao-item.1',
            'ie': 'utf8',
            'initiative_id': 'tbindexz_20170306',
            's': '44',
        }
        file = open('taobao_login_cookies.txt', 'r')
        cookie = file.read()
        self.__cookie = eval(cookie)
        file.close()

    def __reset_cookie(self):
        ul = TaoBaoLogin(s)
        ul.login()
        ul.get_taobao_nick_name()
        file = open('taobao_login_cookies.txt', 'r')
        cookie = file.read()
        self.__cookie = eval(cookie)
        file.close()

    def __safe_get(self, key, infoDict):
        try:
            return infoDict[key]
        except:
            return ''

    def __addParam(self, adds, param):
        if adds in param:
            return param
        return adds + param

    # 输入要爬取的关键字以及要爬取的页数,爬取1页需要10-15秒
    def search(self, keyword, page, path):
        self.__param['q'] = keyword
        if page < 1 or page > 100:
            print('页数小于1或页数大于100')
            return
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/search/'):
            os.mkdir(path + '/search/')
        file = open(path + '/search/' + keyword + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['picLink', 'link', 'title', 'price', 'view_price', 'shop', 'shopLink', 'position', 'sales',
                      'icons']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(page):
            print('正在爬取第' + str(i + 1) + '页')
            self.__param['s'] = str(44 * i)
            url = 'https://s.taobao.com/search?' + urlencode(self.__param)
            if i != 0:
                self.__param['s'] = str(44 * (i - 1))
                self.__headers['referer'] = 'https://s.taobao.com/search?' + urlencode(self.__param)
                self.__param['s'] = str(44 * i)
            rsp = requests.get(url, headers=self.__headers, cookies=self.__cookie)
            info = self.__safe_get(0, re.compile('g_page_config = {(.*?)};').findall(rsp.text))
            if info == '':
                print('重置cookie')
                self.__reset_cookie()
                rsp = requests.get(url, headers=self.__headers, cookies=self.__cookie)
                info = self.__safe_get(0, re.compile('g_page_config = {(.*?)};').findall(rsp.text))
            if info == '':
                print(rsp.text)
                print('ip被封')
            jsonText = json.loads('{' + info + '}')
            items = jsonText['mods']['itemlist']['data']['auctions']
            for item in items:
                icons = item['icon']
                iconStr = ''
                for icon in icons:
                    iconStr += icon['title']
                    if icon != icons[-1]:
                        iconStr += '@#'
                picLink = self.__safe_get('pic_url', item)
                if picLink != '':
                    picLink = 'http:' + picLink
                link = self.__safe_get('detail_url', item)
                if link != '':
                    link = self.__addParam('https:', link)
                shopLink = self.__safe_get('shopLink', item)
                if shopLink != '':
                    shopLink = self.__addParam('https:', shopLink)
                itemDict = {
                    'picLink': picLink,
                    'link': link,
                    'title': item['title'].replace('<span class=H>', '').replace('</span>', ''),
                    'price': item['view_price'],
                    'view_price': item['view_fee'],
                    'shop': item['nick'],
                    'shopLink': shopLink,
                    'position': item['item_loc'],
                    'sales': self.__safe_get('view_sales', item),
                    'icons': iconStr
                }
                writer.writerow(itemDict)
            time.sleep(random.randint(10, 15))

    # 返回商品全部评论
    def get_comments(self, link, path):
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/comments'):
            os.mkdir(path + '/comments')
        time.sleep(random.randint(10, 15))
        headers = {
            'authority': 'detail.tmall.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://www.taobao.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        self.__reset_cookie()
        # 获得标题以及三个id
        response = requests.get(link, headers=headers, cookies=self.__cookie)
        text = response.text
        html = pq(text)
        title = html('#J_DetailMeta > div.tm-clear > div.tb-property > div > div.tb-detail-hd > h1').text()
        print(title)
        file = open(path + '/comments/' + title + '.csv', 'w', encoding='utf-8', newline='')
        fieldnames = ['no', 'comments']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        text = text.replace('\n', '')
        itemId = re.compile('itemId=(.*?)&').findall(text)[0]
        spuId = re.compile('"spuId":(.*?),"').findall(text)[0].replace('"', '')
        sellerId = re.compile('sellerId=(.*?)&').findall(text)[0]
        t = str(time.time() * 1000).replace('.', '_')
        tempParam = {
            'itemId': itemId,
            'spuId': spuId,
            'sellerId': sellerId,
            '_ksTS': t,
            'callback': 'jsonp' + str(int(t.split('_')[1]) + 1)
        }
        refererUrl = response.url
        # 获取所有评论
        param = {
            'itemId': itemId,
            'spuId': spuId,
            'sellerId': sellerId,
            'order': '3',
            'currentPage': 'page从1开始',
            'append': '0',
            'content': '1',
            'tagId': '',
            'posi': '',
            'picture': '',
            'groupId': '',
            'needFold': '0',
            '_ksTS': "str(time.time()*1000).replace('.','_')",
            'callback': 'jsonp604'
        }
        refererUrl = refererUrl.split('&sku_properties')[0]
        headers = {
            'authority': 'rate.tmall.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'accept': '*/*',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'no-cors',
            'referer': refererUrl,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'cna=HWTIFvDu1x4CAXjy/VLvOuKv; hng=CN%7Czh-CN%7CCNY%7C156; lid=%E5%B0%91%E5%B9%B4%E6%97%A0%E7%9F%A5%E4%BA%A6%E6%97%A0%E7%97%9Bht; enc=dBgYrnNxP1aOQYqhMbqNlOgHzDWAyqbkNi0QKtSkhteOYXfWnQi3Nt7GImvC8vUstmJR0%2BOYZ8MTrC9%2FpOWbtA%3D%3D; x5sec=7b22726174656d616e616765723b32223a223038383235356233396465386138323234663537376361616533323332323462434f36627a764946454b48586e722f2b6b61324d78674561444449344d44677a4d6a6b7a4e6a4d374d513d3d227d; sgcookie=D5SLOVolWDbgjg1I8YrLh; t=a2b463636afe181b7bad557a5bcd32c5; uc3=nk2=qjbegxKXYDuCYijLm7uZ1A%3D%3D&vt3=F8dBxd3woSZHJjkN2gc%3D&id2=UUBYjOPeA1Ybtw%3D%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D; tracknick=%5Cu5C11%5Cu5E74%5Cu65E0%5Cu77E5%5Cu4EA6%5Cu65E0%5Cu75DBht; uc4=nk4=0%40qAw6tnUGYvB12yG3UzIeUoqzirXOlagMse8g&id4=0%40U2LK8VerFa7X%2BqzG6mt7biazlUh%2B; lgc=%5Cu5C11%5Cu5E74%5Cu65E0%5Cu77E5%5Cu4EA6%5Cu65E0%5Cu75DBht; _tb_token_=3e3757983e03e; cookie2=1599d19cb2d21f738e6f7f408dfb2eba; l=dB_LqtOqQsqvTfZABOfwCm8r8sQTiIdbzqNrghB9jICPOb5PPA_dWZ2DM7T2CnhV3sGJR3W-27a0BlYaOyUBlZXRFJXn9MpO8d8eR; isg=BODgUFykqnCFdRZof8KGzXYMse6y6cSzj30q11rwJftsVYJ_AvoAQx0j7P1VG3yL'
        }
        t = str(time.time() * 1000).replace('.', '_')
        param['currentPage'] = str(0 + 1)
        param['_ksTS'] = t
        param['callback'] = 'jsonp' + str(int(t.split('_')[1]) + 1)
        url = "https://rate.tmall.com/list_detail_rate.htm?" + urlencode(param)
        rsp = requests.get(url, headers=headers)
        total = re.compile('"total":(.*?),').findall(rsp.text)[0]
        total = eval(total)
        print('共有' + str(total) + '页')
        counts = int(total / 20) + 1
        people = 0
        for i in range(counts):
            print('正在爬取评论页的第' + str(i + 1) + '页')
            t = str(time.time() * 1000).replace('.', '_')
            param['currentPage'] = str(i + 1)
            param['_ksTS'] = t
            param['callback'] = 'jsonp' + str(int(t.split('_')[1]) + 1)
            url = "https://rate.tmall.com/list_detail_rate.htm?" + urlencode(param)
            rsp = requests.get(url, headers=headers)
            print(rsp.text)
            first = rsp.text.split('"searchinfo"')[0]
            second = first.split('"rateList"')[1]
            finLists = second[1:-1]
            comments = re.compile(',"rateContent":"(.*?)",').findall(finLists)
            if comments == '':
                print(rsp.text)
            for comment in comments:
                commentsDict = {
                    'no': str(people),
                    'comments': comment
                }
                print(commentsDict)
                people += 1
                try:
                    writer.writerow(commentsDict)
                except:
                    commentsDict = {
                        'no': str(people - 1),
                        'comments': ''
                    }
                    writer.writerow(commentsDict)
            # time.sleep(random.randint(10, 15))
        file.close()


if __name__ == '__main__':
    t = TaoBao()
    # 进行搜索，第一个参数为关键字，第二个参数为总共要爬取多少页，第三个参数为存储的位置
    t.search('笔记本电脑', 100, 'data')
    # 获取商品的评论，第一个参数为商品的链接，第二个参数为存储的位置
    # t.get_comments('https://detail.tmall.com/item.htm?id=525248995106&ali_refid=a3_430583_1006:1110721174:N:f4K9WgbkZ2hBS5Oy+VVogw==:19b0f178b3146771d8801c9861e4af31&ali_trackid=1_19b0f178b3146771d8801c9861e4af31&spm=a230r.1.14.1&sku_properties=5919063:6536025','data')
