# -*- coding: UTF-8 –*-
'''
今日头条爬虫，现可以进行搜索，爬取头条文章以及爬取图片
作者：洪韬
时间：2020/2/23
'''
from urllib.parse import quote, urlencode
from pyquery import PyQuery as pq
import requests
import hashlib
import execjs
import json
import time
import csv
import re
import os


class TouTiaoCrawl:
    def __init__(self):
        self.__searchParam = {
            'aid': '24',
            'keyword': 'keyword',
            'app_name': 'web_search',
            'offset': '40',
            'format': 'json',
            'autoload': 'true',
            'count': '20',
            'cur_tab': '1',
            'from': 'search_tab',
            'pd': 'synthesis',
            'timestamp': '1581675080465'
        }
        self.__searchHeaders = {
            'authority': 'www.toutiao.com',
            'accept': 'application/json, text/javascript',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.toutiao.com/search/?keyword=' + quote('关键字'),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        sessionIdText = '''
                function r(e) {
                        for (var t = ""; t.length < e; t += Math.random().toString(36).substr(2))
                            ;
                        return t.substr(0, e)
                    }
                function result(){
                    return "" + r(9) + (new Date).getTime()
                }
                '''
        webIdText = '''
                function test() {
                    var t = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".split(""),
                    e = t.length,
                    n = (new Date).getTime().toString(36),
                    i = [];
                    i[8] = i[13] = i[18] = i[23] = "_",
                    i[14] = "4";
                    for (var a, r = 0; r < 36; r++)
                        i[r] || (a = 0 | Math.random() * e,
                        i[r] = t[19 == r ? 3 & a | 8 : a]);
                    return n + "_" + i.join("")
                }
                '''
        self.__sessionIdJS = execjs.compile(sessionIdText)
        self.__webIdJs = execjs.compile(webIdText)

        # 获得tt_webid
        self.__tt_webidUrl = "https://www.toutiao.com/"
        self.__tt_webidHeaders = {
            'authority': 'www.toutiao.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '__tasessionId=' + self.__sessionIdJS.call('result')
        }

        response = requests.get(self.__tt_webidUrl, headers=self.__tt_webidHeaders)

        self.__tt_webIdCookies = requests.utils.dict_from_cookiejar(response.cookies)
        sid = self.__sessionIdJS.call('result')
        # 获得csrftoken
        self.__csrfUrl = "https://www.toutiao.com/api/article/user_log/?c=/&sid=" + sid + "&type=pageview&t=" + str(
            int(time.time() * 1000))
        self.__csrfHeaders = {
            'authority': 'www.toutiao.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'no-cors',
            'referer': 'https://www.toutiao.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '__tasessionId=' + sid + '; tt_webid=' + self.__tt_webIdCookies[
                'tt_webid'] + '; s_v_web_id=' + self.__webIdJs.call('test') + '; WEATHER_CITY=' + quote('北京')
        }

        response = requests.get(self.__csrfUrl, headers=self.__csrfHeaders)
        self.__csrftokenCookie = requests.utils.dict_from_cookiejar(response.cookies)
        self.__searchCookie = {
            '__tasessionId': self.__sessionIdJS.call('result'),
            's_v_web_id': self.__webIdJs.call('test'),
            'csrftoken': self.__csrftokenCookie['csrftoken'],
            'tt_webid': self.__tt_webIdCookies['tt_webid'],
            'WEATHER_CITY': quote('北京')
        }
        self.__max_behot_time = 0

    def __getAsCp(self):
        text = '''
        function getparam() {
                var t = Math.floor((new Date).getTime() / 1e3)
                  , s = t.toString(16).toUpperCase();
                  return {t,s};
        }
        '''
        m = hashlib.md5()
        jsText = execjs.compile(text)
        ts = jsText.call('getparam')
        s = ts['s']
        encodeT = str(ts['t']).encode(encoding='utf-8')
        m.update(encodeT)
        str_md5 = m.hexdigest()
        e = str_md5.upper()
        if 8 != len(s):
            return {'as': "479BB4B7254C150", 'cp': "7E0AC8874BB0985"}
        i = e[0:5]
        o = e[-5:]
        a = ""
        for l in range(5):
            a += i[l] + s[l]
        n = ""
        for c in range(5):
            n += s[c + 3] + o[c]
        return {'as': "A1" + a + s[-3:], 'cp': s[0:3] + n + "E1"}

    def __resetCookie(self):
        self.__tt_webidHeaders['cookie'] = '__tasessionId=' + self.__sessionIdJS.call('result')
        response = requests.get(self.__tt_webidUrl, headers=self.__tt_webidHeaders)

        self.__tt_webIdCookies = requests.utils.dict_from_cookiejar(response.cookies)
        sid = self.__sessionIdJS.call('result')
        self.__csrfUrl = "https://www.toutiao.com/api/article/user_log/?c=/&sid=" + sid + "&type=pageview&t=" + str(
            int(time.time() * 1000))
        self.__csrfHeaders['cookie'] = '__tasessionId=' + sid + '; tt_webid=' + self.__tt_webIdCookies[
            'tt_webid'] + '; s_v_web_id=' + self.__webIdJs.call('test') + '; WEATHER_CITY=' + quote('北京')
        response = requests.get(self.__csrfUrl, headers=self.__csrfHeaders)
        self.__csrftokenCookie = requests.utils.dict_from_cookiejar(response.cookies)
        self.__searchCookie = {
            '__tasessionId': self.__sessionIdJS.call('result'),
            's_v_web_id': self.__webIdJs.call('test'),
            'csrftoken': self.__csrftokenCookie['csrftoken'],
            'tt_webid': self.__tt_webIdCookies['tt_webid'],
            'WEATHER_CITY': quote('北京')
        }

    def __safe_get(self, key, dict):
        try:
            return dict[key]
        except:
            return ''

    # 返回搜索结果，格式以链接、标题、来源以及时间
    def search(self, keyword, path):
        self.__searchUrl = 'https://www.toutiao.com/api/search/content/?'
        self.__searchParam['keyword'] = quote(keyword)
        self.__searchHeaders['referer'] = 'https://www.toutiao.com/search/?keyword=' + quote(keyword)
        count = 0
        totalLists = []
        total = 0
        while True:
            print('正在爬取第' + str(count + 1) + '页')
            self.__searchParam['offset'] = str(20 * count)
            self.__searchParam['timestamp'] = str(int(time.time() * 1000))
            url = self.__searchUrl
            for k in self.__searchParam:
                url = url + k + '=' + self.__searchParam[k]
                if k != 'timestamp':
                    url += '&'
            count += 1
            try:
                self.__searchHeaders['cookie'] = '__tasessionId=' + self.__searchCookie[
                    '__tasessionId'] + '; tt_webid=' + self.__searchCookie['tt_webid'] + '; WEATHER_CITY=' + \
                                                 self.__searchCookie['WEATHER_CITY'] + '; tt_webid=' + \
                                                 self.__searchCookie[
                                                     'tt_webid'] + '; csrftoken=' + self.__searchCookie[
                                                     'csrftoken'] + '; s_v_web_id=' + self.__searchCookie['s_v_web_id']
                time.sleep(2)
                rsp = requests.get(url, headers=self.__searchHeaders)
                jsonText = json.loads(rsp.text)
                dataes = jsonText['data']
                if dataes == None:
                    print('爬取结束')
                    break
                for data in dataes:
                    infoDict = {}
                    title = self.__safe_get('title', data)
                    if title == '':
                        merge_articles = self.__safe_get('merge_article', data)
                        displays = self.__safe_get('display', data)
                        if merge_articles != '':
                            for merge_article in merge_articles:
                                title = self.__safe_get('title', merge_article)
                                if title != '':
                                    link = self.__safe_get('open_url', merge_article)
                                    if link == '':
                                        link = self.__safe_get('seo_url', merge_article)
                                    if link != '':
                                        link = 'https://www.toutiao.com' + link
                                    source = self.__safe_get('source', merge_article)
                                    comments = self.__safe_get('comments_count', merge_article)
                                    datetime = self.__safe_get('datetime', merge_article)
                                    infoDict['link'] = link
                                    infoDict['title'] = title
                                    infoDict['source'] = source
                                    infoDict['comments'] = comments
                                    infoDict['datetime'] = datetime
                                    totalLists.append(infoDict)
                                    total += 1
                        elif displays != '':
                            for display in displays:
                                title = self.__safe_get('title', display)
                                if title != '':
                                    link = self.__safe_get('open_url', display)
                                    if link == '':
                                        link = self.__safe_get('seo_url', merge_article)
                                    if link != '':
                                        link = 'https://www.toutiao.com' + link
                                    source = self.__safe_get('source', display)
                                    comments = self.__safe_get('comments_count', display)
                                    datetime = self.__safe_get('datetime', display)
                                    infoDict['link'] = link
                                    infoDict['title'] = title
                                    infoDict['source'] = source
                                    infoDict['comments'] = comments
                                    infoDict['datetime'] = datetime
                                    totalLists.append(infoDict)
                                    total += 1
                        else:
                            continue
                    else:
                        link = self.__safe_get('open_url', data)
                        if link != '':
                            link = 'https://www.toutiao.com' + link
                        source = self.__safe_get('source', data)
                        comments = self.__safe_get('comments_count', data)
                        datetime = self.__safe_get('datetime', data)
                        infoDict['link'] = link
                        infoDict['title'] = title
                        infoDict['source'] = source
                        infoDict['comments'] = comments
                        infoDict['datetime'] = datetime
                        totalLists.append(infoDict)
                        total += 1
            except:
                print('出错了,换cookie')
                self.__resetCookie()
                if count != 0:
                    count -= 1
        totalDicts = {'type': 'search',
                      'keyword': keyword,
                      'data': totalLists}
        jsonText = json.dumps(totalDicts, ensure_ascii=False)
        if isinstance(jsonText, str):
            jsonText = json.loads(jsonText)
        name = jsonText['type']
        data = jsonText['data']
        fieldnames = []
        for k in data[0]:
            fieldnames.append(k)
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/' + name):
            # 创建文件
            os.mkdir(path + '/' + name)
        file = open(path + '/' + name + '/' + jsonText['keyword'] + '.csv', 'w', encoding='utf-8', newline='')
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for dict in data:
            writer.writerow(dict)

    # 根据链接返回新闻,格式必须为https://www.toutiao.com/a....../,保存在
    def get_article(self, link, path):
        headers = {
            'authority': 'www.toutiao.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        headers['cookie'] = '__tasessionId=' + self.__searchCookie['__tasessionId'] + '; tt_webid=' + \
                            self.__searchCookie[
                                'tt_webid'] + '; WEATHER_CITY=' + self.__searchCookie['WEATHER_CITY'] + '; tt_webid=' + \
                            self.__searchCookie[
                                'tt_webid'] + '; csrftoken=' + self.__searchCookie['csrftoken'] + '; s_v_web_id=' + \
                            self.__searchCookie['s_v_web_id']
        try:
            rsp = requests.get(link, headers=headers)
        except:
            print('出错了！换Cookie')
            self.__resetCookie()
            self.get_article(link, path)
        title = self.__safe_get(0, re.compile("      title: '(.*?)'").findall(rsp.text)).replace('&quot;', '')
        source = self.__safe_get(0, re.compile("        source: '(.*?)'").findall(rsp.text))
        time = self.__safe_get(0, re.compile("        time: '(.*?)'").findall(rsp.text))
        content = self.__safe_get(0, re.compile("      content: '(.*?)'").findall(rsp.text)).replace('&quot;', '')
        content = eval("u" + "\'" + content + "\'").replace('&#x3D;', '=').replace('\\u003E', '>').replace('\\',
                                                                                                           '').replace(
            '\n', '')
        imgUrls = re.compile('<img src=(.*?) img').findall(content)
        imgs = re.compile('<img(.*?)>').findall(content)
        for img in imgs:
            content = content.replace('<img' + img + '>', '')
        html = pq(content)
        text = html.text()
        finArticle = title + '\n' + source + ' ' + time + '\n' + text
        print('正在爬取' + title)
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/' + 'article'):
            # 创建文件
            os.mkdir(path + '/' + 'article')
        if not os.path.exists(path + '/article/' + title):
            os.mkdir(path + '/article/' + title)
        file = open(path + '/article/' + title + '/textOnly.txt', 'w', encoding='utf-8')
        file.write(finArticle)
        file.close()
        length = len(imgUrls)
        if length != 0:
            if not os.path.exists(path + '/article/' + title + '/image'):
                os.mkdir(path + '/article/' + title + '/image')
            for i in range(length):
                rsp = requests.get(imgUrls[i])
                file = open(path + '/article/' + title + '/image/' + str(i) + '.jpg', 'wb')
                file.write(rsp.content)
                file.close()

    # 根据链接获取其中的照片
    def get_pricture(self, link, path):
        headers = {
            'authority': 'www.toutiao.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        headers['cookie'] = '__tasessionId=' + self.__searchCookie['__tasessionId'] + '; tt_webid=' + \
                            self.__searchCookie[
                                'tt_webid'] + '; WEATHER_CITY=' + self.__searchCookie['WEATHER_CITY'] + '; tt_webid=' + \
                            self.__searchCookie[
                                'tt_webid'] + '; csrftoken=' + self.__searchCookie['csrftoken'] + '; s_v_web_id=' + \
                            self.__searchCookie['s_v_web_id']
        try:
            rsp = requests.get(link, headers=headers)
        except:
            print('出错了！换Cookie')
            self.__resetCookie()
            self.get_pricture(link, path)
        content = rsp.text.replace('\n', '')
        info = self.__safe_get(0, re.compile('BASE_DATA.galleryInfo = {(.*?)}').findall(content))
        if info == '':
            print('ip被封或链接不正确')
            return
        title = self.__safe_get(0, re.compile("title: '(.*?)',").findall(info))
        print('正在爬取' + title)
        pictureUrls = self.__safe_get(0, re.compile('gallery: (.*?)\n').findall(rsp.text))
        noNameNumber = 0
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/pictures'):
            os.mkdir(path + '/pictures')
        if pictureUrls != '':
            if title != '':
                if not os.path.exists(path + '/pictures/' + title):
                    os.mkdir(path + '/pictures/' + title)
            else:
                if not os.path.exists(path + '/pictures/noname'):
                    os.mkdir(path + '/pictures/noname')
                while True:
                    if not os.path.exists(path + '/pictures/noname/' + str(noNameNumber)):
                        os.mkdir(path + '/pictures/noname/' + str(noNameNumber))
                        break
                    noNameNumber += 1
            pictureUrls = pictureUrls[:-1]
            pictureUrls = pictureUrls.replace('\\u002F', '/').replace('\\', '').replace('JSON.parse(', '').replace(')',
                                                                                                                   '')
            urlDict = eval(pictureUrls[1:-1])
            urlItems = urlDict['sub_images']
            count = 0
            if title != '':
                path = path + '/pictures/' + title + '/'
            else:
                path + '/pictures/noname/' + str(noNameNumber) + '/'
            for item in urlItems:
                url = item['url']
                file = open(path + str(count) + '.jpg', 'wb')
                count += 1
                rsp = requests.get(url)
                file.write(rsp.content)
                file.close()

    # 得到推荐的第1000条新闻
    def get_news(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/news'):
            # 创建文件
            os.mkdir(path + '/news')
        year=time.localtime(time.time()).tm_year
        month=time.localtime(time.time()).tm_mon
        day=time.localtime(time.time()).tm_mday
        file=open(path+'/news/'+str(year)+'-'+str(month)+'-'+str(day)+'.csv','w',encoding='utf-8',newline='')
        fieldnames=['title','source','comments','tag','abstract','time']
        writer=csv.DictWriter(file,fieldnames)
        writer.writeheader()
        for i in range(100):
            time.sleep(1)
            print('正在爬取第'+str(i+1)+'页')
            ascpDict = self.__getAsCp()
            url = "https://www.toutiao.com/api/pc/feed/"
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
                "referer": "https://www.toutiao.com/"
            }
            headers['cookie'] = '__tasessionId=' + self.__searchCookie['__tasessionId'] + '; tt_webid=' + \
                                self.__searchCookie[
                                    'tt_webid'] + '; WEATHER_CITY=' + self.__searchCookie[
                                    'WEATHER_CITY'] + '; tt_webid=' + \
                                self.__searchCookie[
                                    'tt_webid'] + '; csrftoken=' + self.__searchCookie['csrftoken'] + '; s_v_web_id=' + \
                                self.__searchCookie['s_v_web_id']

            if self.__max_behot_time == 0:
                behot_time = "min_behot_time"
            else:
                behot_time = "max_behot_time"
            params = {
                behot_time: self.__max_behot_time,
                "category": "__all__",
                "utm_source": "toutiao",
                "widen": "1",
                "tadrequire": "true",
                "as": "",
                "cp": "",
            }
            params['as'] = ascpDict['as']
            params['cp'] = ascpDict['cp']
            decode_url = url + "?" + urlencode(params)
            decode_url = decode_url.replace("com/", "com/toutiao/")
            data = {
                "url": quote(decode_url)
            }
            _signature = requests.post('http://121.40.96.182:4007/get_sign', data=data).json()['_signature']
            params["_signature"] = _signature
            resp = requests.get(url, headers=headers, params=params)
            jsonText = json.loads(resp.text)
            self.__max_behot_time = jsonText['next']['max_behot_time']
            all_data = jsonText['data']
            itemDict = {}
            for data in all_data:
                itemDict['title'] = self.__safe_get('title', data)
                itemDict['source'] = self.__safe_get('source', data)
                itemDict['comments'] = self.__safe_get('comments_count', data)
                itemDict['tag'] = self.__safe_get('chinese_tag', data)
                itemDict['abstract'] = self.__safe_get('abstract', data)
                behot_time = self.__safe_get('behot_time', data)
                local_time = time.localtime(behot_time)
                real_time = str(local_time.tm_year) + '/' + str(local_time.tm_mon) + '/' + str(
                    local_time.tm_mday) + ' ' + str(local_time.tm_hour) + ':' + str(local_time.tm_min)
                itemDict['time']=real_time
                writer.writerow(itemDict)
        file.close()
if __name__ == '__main__':
    app = TouTiaoCrawl()
    # 搜索：第一个参数为关键字，第二个为存储的位置
    # app.search('复工', 'data')
    # 得到文章，第一个参数为链接，第二个参数为存储的位置
    # app.get_article('https://www.toutiao.com/a6796467018682860043/', 'data')
    # 得到图片.第一个参数为链接，第二个参数为存储的位置
    # app.get_pricture('https://www.toutiao.com/a6771643217868751374/', 'data')
    #得到首页推荐的1000条新闻
    #app.get_news('data')