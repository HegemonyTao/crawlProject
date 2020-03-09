from const import GameTypes, TypeUrls
import requests
from pyquery import PyQuery as pq
from urllib.parse import quote



def get_types():
    url = "https://store.steampowered.com/tag/browse/"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    response = requests.get(url, headers=headers)
    html = pq(response.text)
    items = html('#tag_browse_global>div').items()
    types = []
    for item in items:
        types.append(item.text())
    return types

def get_urls():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://store.steampowered.com/tags/zh-cn/%E7%8B%AC%E7%AB%8B/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    for signalType in GameTypes:
        errorItems = []
        if signalType not in TypeUrls:
            url = 'https://store.steampowered.com/tags/zh-cn/' + quote(signalType) + '/#p=0&tab=ConcurrentUsers'
            headers['Referer'] = 'https://store.steampowered.com/tags/zh-cn/' + quote(signalType) + '/'
            try:
                response = requests.get(url, headers=headers)
            except:
                print('出错了，出错的类型为:')
                if signalType not in errorItems:
                    errorItems.append(signalType)
                print(errorItems)
                continue
            html = pq(response.text)
            url = html('#ConcurrentUsersTable > div:nth-child(3) > a').attr('href')
            TypeUrls[signalType] = url
    return TypeUrls