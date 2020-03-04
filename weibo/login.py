import base64, time, re, rsa, random, json, logging
from binascii import b2a_hex
from urllib import parse


class Weibo():
    def __init__(self, user, password, s):
        self.user = user
        self.password = password
        # 用户名进过base64加密
        self.su = base64.b64encode(self.user.encode()).decode()
        self.session = s
        self.session.get('https://login.sina.com.cn/signup/signin.php')

    def pre_log(self):
        # 预登陆，获取信息
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(
            parse.quote(self.su), int(time.time() * 1000))
        try:
            res = self.session.get(url).text
            res = re.findall(r"({.*})", res)[0]
            self.res = json.loads(res)
            self.nonce = self.res["nonce"]
            self.pubkey = self.res["pubkey"]
            self.rsakv = self.res["rsakv"]
            self.servertime = self.res["servertime"]
            # print(self.nonce,'\n',self.pubkey,'\n',self.rsakv,'\n',self.servertime)
        except Exception as error:
            logging.error("WeiBoLogin pre_log error: %s", error)

    def get_sp(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey, 16), int('10001', 16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = rsa.encrypt(message.encode(), publickey)
        return b2a_hex(self.sp)

    def login(self):
        data = {
            'entry': 'account',
            'gateway': '1',
            'from': 'null',
            'savestate': '30',
            'useticket': '0',
            'vsnf': '1',
            'su': self.su,
            'service': 'account',
            'servertime': self.servertime,
            'nonce': self.nonce,
            'pwencode': 'rsa2',
            'rsakv': self.rsakv,
            'sp': self.get_sp(),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': random.randint(1, 100),
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'
        }
        # print(self.res)
        # 验证码 :showpin为1时出现验证码
        if self.res["showpin"] == 1:
            url = "http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (int(time.time()), self.res["pcid"])
            file_out = open('captcha.jpg', 'wb')
            file_out.write(self.session.get(url).content)
            file_out.close()
            code = input("请输入验证码:")
            data["pcid"] = self.res["pcid"]
            data["door"] = code

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        json_data = self.session.post(url, data=data).json()
        # 判断post登录是否成功
        if json_data['retcode'] == '0':
            params = {
                'ticket': json_data['ticket'],
                'ssosavestate': int(time.time()),
                'callback': 'sinaSSOController.doCrossDomainCallBack',
                'scriptId': 'ssoscript0',
                'client': 'ssologin.js(v1.4.19)',
                '_': int(time.time() * 1000)
            }
            # 二次登录网页验证
            url = 'https://passport.weibo.com/wbsso/login'
            res = self.session.get(url, params=params)
            json_data1 = json.loads(re.search(r'({"result":.*})', res.text).group())
            # 判断是否登录成功
            if json_data1['result'] is True:
                print('登录成功，你的用户名是:' + json_data1['userinfo']['displayname'])
            else:
                print('登录失败')
        else:
            print('登录成功')

    def main(self):
        self.pre_log()
        self.login()
