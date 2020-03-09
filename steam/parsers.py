from pyquery import PyQuery as pq
from const import GameTypes, TypeUrls
import re
import requests
import json


def get_page(gameType, page, count):
    BaseHeader = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    if gameType not in TypeUrls:
        raise Exception('没有找到该类型')
        return
    if TypeUrls[gameType] == None:
        url = 'https://store.steampowered.com/tags/zh-cn/' + quote(gameType) + '/#p=0&tab=ConcurrentUsers'
        headers = BaseHeader
        headers[Referer] = 'https://store.steampowered.com/tags/zh-cn/' + quote(gameType) + '/',
        response = requests.get(url, headers=headers)
        html = pq(response.text)
        text = html('#tab_content_ConcurrentUsers>div>div')
        itemLists = get_details_2(text, gameType)
        itemDict = {
            'count': len(itemLists),
            'page': 1,
            'limit': len(itemLists),
            'data': itemLists
        }
        return itemDict
    tagUrl = TypeUrls[gameType]
    tag = re.compile('&tags=(.*?)&').findall(tagUrl)[0]
    BaseHeader['Referer'] = 'https://store.steampowered.com/search/?&tags=' + tag
    try:
        url = "https://store.steampowered.com/search/results/?query&start=" + str((page - 1) * count) + "&count=" + str(
            count) + "&dynamic_data=&sort_by=_ASC&tags=" + tag + "&snr=1_7_7_240_7&infinite=1"
        print(url)
        response = requests.get(url, BaseHeader)
    except:
        raise Exception('页数小于1或页数过大')
        return
    total = json.loads(response.text)['total_count']
    gamesInfo = get_details(response.text)
    itemDict = {
        'count': total,
        'page': page,
        'limit': len(gamesInfo),
        'data': gamesInfo
    }
    return itemDict


def get_details(text):
    gamesInfo = []
    jsonText = json.loads(text)
    resultText = jsonText['results_html']
    html = pq(resultText)
    items = html('a').items()
    for item in items:
        url = item.attr('href')
        id = re.compile('https://store.steampowered.com/(.*?)/(.*?)/').findall(url)[0][1]
        imgUrl = item('div.col.search_capsule > img').attr('src')
        p = item('div.responsive_search_name_combined > div.col.search_name.ellipsis > p>span').items()
        platform = ''
        for pItem in p:
            platform += pItem.attr('class').replace('platform_img ', '') + ' '
        if platform != '':
            platform = platform[:-1]
        discount = item(
            'div.responsive_search_name_combined > div.col.search_price_discount_combined.responsive_secondrow > div.col.search_discount.responsive_secondrow > span').text()
        origin_now_price = item(
            'div.responsive_search_name_combined > div.col.search_price_discount_combined.responsive_secondrow > div.col.search_price.responsive_secondrow').text().replace(
            '\n', '#')
        if discount != '':
            originPrice = origin_now_price.split('#')[0]
            nowPrice = origin_now_price.split('#')[2].replace('#', '')
        else:
            originPrice = nowPrice = origin_now_price.replace('#', '').replace('↵', '')
        if '¥' not in nowPrice:
            nowPrice = 'Free to play'
        if '¥' not in originPrice:
            originPrice = 'Free to play'
        comment = item(
            'div.responsive_search_name_combined > div.col.search_reviewscore.responsive_secondrow > span').attr(
            'data-tooltip-html')
        if comment != None:
            comment = comment.replace('<br>', '--')
        else:
            comment = '评论人数不足'
        gameInfo = {
            'imgUrl': imgUrl,
            'url': url,
            'id': id,
            'title': item('div.responsive_search_name_combined > div.col.search_name.ellipsis > span').text(),
            'time': item(
                'div.responsive_search_name_combined > div.col.search_released.responsive_secondrow').text(),
            'comment': comment,
            'discount': discount,
            'originPrice': originPrice,
            'nowPrice': nowPrice,
            'platform': platform
        }
        gamesInfo.append(gameInfo)
    return gamesInfo


def get_details_2(html, gameType):
    gamesInfo = []
    baseHeader = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    items = html('a').items()
    for item in items:
        url = item.attr('href')
        id = re.compile('https://store.steampowered.com/(.*?)/(.*?)/').findall(url)[0][1]
        comment_time = 'https://store.steampowered.com/apphoverpublic/' + id + '?review_score_preference=0&l=schinese&pagev6=true'
        headers = baseHeader
        headers['Referer'] = 'https://store.steampowered.com/tags/zh-cn/' + quote(gameType) + '/',
        response = requests.get(comment_time, headers=headers)
        html = pq(response.text)
        time = html('div.hover_release').text().replace('发行于: ', '')
        comment = html('div.hover_review_summary').text().replace('总体用户评测：', '').replace('\n', '')
        p = item('div.tab_item_content > div.tab_item_details > span').items()
        imgUrl = item('div.tab_item_cap > img').attr('src')
        platform = ''
        for pItem in p:
            platform += pItem.attr('class').replace('platform_img ', '') + ' '
        if platform != '':
            platform = platform[:-1]
        discount = item('div.discount_block.tab_item_discount > div.discount_pct').text()
        if discount != '':
            originPrice = item(
                'div.discount_block.tab_item_discount > div.discount_prices > div.discount_original_price').text()
            nowPrice = item(
                'div.discount_block.tab_item_discount > div.discount_prices > div.discount_final_price').text()
        else:
            originPrice = nowPrice = item('div.discount_block.tab_item_discount.no_discount > div > div').text()
        if '¥' not in nowPrice:
            originPrice = nowPrice = 'Free to play'
        if '¥' not in nowPrice:
            nowPrice = 'Free to play'
        if '¥' not in originPrice:
            originPrice = 'Free to play'
        gameInfo = {
            'imgUrl': imgUrl,
            'url': url,
            'id': id,
            'title': item('div.tab_item_content > div.tab_item_name').text(),
            'time': time,
            'comment': comment,
            'discount': discount,
            'originPrice': originPrice,
            'nowPrice': nowPrice,
            'platform': platform
        }
        gamesInfo.append(gameInfo)
    return gamesInfo

def getGameById(id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Referer': 'https://store.steampowered.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    response = requests.get('https://store.steampowered.com/app/' + str(id) + '/' ,headers=headers)
    html=pq(response.text)
    discount=html('#game_area_purchase > div > div > div.game_purchase_action > div > div.discount_block.game_purchase_discount > div.discount_pct').text()
    if discount=='':
        originPrice = nowPrice=html('#game_area_purchase > div > div > div.game_purchase_action > div > div.game_purchase_price.price').text()
    else:
        originPrice=html('#game_area_purchase > div > div > div.game_purchase_action > div > div.discount_block.game_purchase_discount > div.discount_prices > div.discount_original_price').text()
        nowPrice=html('#game_area_purchase > div > div > div.game_purchase_action > div > div.discount_block.game_purchase_discount > div.discount_prices > div.discount_final_price').text()
    if '¥' not in nowPrice:
        nowPrice = 'Free to play'
    if '¥' not in originPrice:
        originPrice = 'Free to play'
    p=html('body > div.responsive_page_frame.with_header > div.responsive_page_content > div.responsive_page_template_content > div.game_page_background.game > div.page_content_ctn > div:nth-child(6) > div.leftcol.game_description_column > div.game_page_autocollapse.sys_req > div.sysreq_tabs>div').items()
    platform=''
    for pItem in p:
        if 'sysreq_tab' in str(pItem):
            platform += pItem.attr('data-os')+ ' '
    if platform != '':
        platform = platform[:-1]
    else:
        platform='win'
    itemDict={
        'imgUrl':html('#game_highlights > div.rightcol > div > div.game_header_image_ctn > img').attr('src'),
        'url':response.url,
        'title':html('body > div.responsive_page_frame.with_header > div.responsive_page_content > div.responsive_page_template_content > div.game_page_background.game > div.page_content_ctn > div.page_title_area.game_title_area.page_content > div.breadcrumbs > div.blockbg > a:nth-child(4) > span').text(),
        'time':html('#game_highlights > div.rightcol > div > div.glance_ctn_responsive_left > div > div.release_date > div.date').text(),
        'comment':html('#game_highlights > div.rightcol > div > div.glance_ctn_responsive_left > div > div.user_reviews_summary_row > div.summary.column').text(),
        'discount':discount,
        'originPrice':originPrice,
        'nowPrice':nowPrice,
        'platform':platform
    }
    return itemDict