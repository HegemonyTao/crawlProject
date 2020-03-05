# -*- coding: UTF-8 –*-
'''
有道翻译爬虫
作者：洪韬
时间：2020/3/5
'''
import requests
import execjs
import hashlib
import json
from urllib.parse import quote
from urllib.parse import unquote
class YouDaoCrawl:
    def __init__(self):
        self.__headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://fanyi.youdao.com',
            'Referer': 'http://fanyi.youdao.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
    def __read_cookie(self):
        file=open('cookie.txt','r')
        cookies=file.read()
        cookie_split=cookies.split(';')
        cookieDict={}
        for cookie in cookie_split:
            k_v=cookie.split('=')
            cookieDict[k_v[0]]=k_v[1]
        return cookieDict
    def __reset_cookie(self):
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        rsp=requests.get('http://fanyi.youdao.com/',headers=headers)
        cookie=requests.utils.dict_from_cookiejar(rsp.cookies)
        cookie['OUTFOX_SEARCH_USER_ID_NCOO']=str(execjs.eval('2147483647 * Math.random()'))
        cookie['___rl__test__cookies']=str(execjs.eval('(new Date).getTime()'))
        cookieStr=''
        for k in cookie:
            cookieStr+=k+'='+cookie[k]
            if k!='___rl__test__cookies':
                cookieStr+='&'
        file=open('cookie.txt','w')
        file.write(cookieStr)
        file.close()
    def __encry(self,param):
        md5=hashlib.md5(param.encode("utf-8"))
        return md5.hexdigest()
    def trans(self,words):
        url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
        i=execjs.eval('"" + (new Date).getTime()+parseInt(10 * Math.random(), 10)')
        words=quote(words)
        md5Str="fanyideskweb" + words + i + "Nw(nmmbP%A-r6U3EUn]Aj"
        appVersion="5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        salt=str(execjs.eval('(new Date).getTime()'))
        data={
            'i': words,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': self.__encry(md5Str),
            'ts': salt[:-1],
            'bv': self.__encry(appVersion),
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }
        cookies=self.__read_cookie()
        response=requests.post(url,headers=self.__headers,data=data,cookies=cookies)
        jsonText=json.loads(response.text)
        tgt=jsonText['translateResult'][0][0]['tgt']
        return unquote(tgt)
if __name__=='__main__':
    app=YouDaoCrawl()
    #参数为要翻译的句子或段落
    print(app.trans('hello'))