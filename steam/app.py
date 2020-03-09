# -*- coding: UTF-8 –*-
'''
steam爬虫，现可以根据游戏类型爬取相应游戏，根据游戏的id爬取游戏信息
作者：洪韬
时间：2020/3/9
'''
from parsers import get_page, getGameById

if __name__ == '__main__':
# count >= 25
# result = get_page(gameType='独立', page=2, count=30)
    result=getGameById(id=407130)
    print(result)
