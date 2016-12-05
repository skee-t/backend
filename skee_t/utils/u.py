#! -*- coding: UTF-8 -*-
import datetime
import hashlib
import random
import urllib
import uuid
import time

import re
import HTMLParser

from skee_t.conf import CONF
# from html.parser import HTMLParser

__author__ = 'rensikun'


class U:
    def __init__(self):
        pass

    @staticmethod
    def timeStr():
        return datetime.datetime.now().strftime("%Y-%m-%-d %H:%M")

    @staticmethod
    def gen_order_no():
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'-'+U.gen_uuid()[0:13]

    @staticmethod
    def gen_refund_id():
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")+U.gen_uuid()[0:5].upper()

    @staticmethod
    def gen_uuid():
        return str(uuid.uuid4()).replace('-','')

    @staticmethod
    def sign_md5(mydict):
        str_sign_temp = '&'.join([key+"="+mydict[key] for key in sorted(mydict.keys())]) \
                        + "&key=" + CONF.wxp.key
        mx6s = hashlib.md5()
        mx6s.update(str_sign_temp)
        return mx6s.hexdigest().upper()

    @staticmethod
    def sign_sha1(mydict):
        str_sign_temp = '&'.join([key+"="+mydict[key] for key in sorted(mydict.keys())])
        sha1 = hashlib.sha1()
        sha1.update(str_sign_temp)
        return sha1.hexdigest()

    @staticmethod
    def gen_auth_code_num():
        code_list = []
        for i in range(6):
            random_num = random.randint(0, 9) # 随机生成0-9的数字
            code_list.append(str(random_num))
        verification_code = ''.join(code_list)
        return verification_code

    @staticmethod
    def gen_auth_code():
        code_list = []
        for i in range(2):
            random_num = random.randint(0, 9) # 随机生成0-9的数字
            # 利用random.randint()函数生成一个随机整数a，使得65<=a<=90
            # 对应从“A”到“Z”的ASCII码
            a = random.randint(65, 90)
            b = random.randint(97, 122)
            random_uppercase_letter = chr(a)
            random_lowercase_letter = chr(b)
            code_list.append(str(random_num))
            code_list.append(random_uppercase_letter)
            code_list.append(random_lowercase_letter)
        verification_code = ''.join(code_list)
        return verification_code

    @staticmethod
    def filter_emoji(desstr,restr=''):
        '''
        过滤表情
        '''
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    @staticmethod
    def str_2_emoji(emoji_str):
        '''
        把字符串转换为表情
        '''
        if not emoji_str:
            return emoji_str
        h = HTMLParser.HTMLParser()
        emoji_str = h.unescape(h.unescape(emoji_str))
        #匹配u"\U0001f61c"和u"\u274c"这种表情的字符串
        co = re.compile(ur"u[\'\"]\\[Uu]([\w\"]{9}|[\w\"]{5})")
        pos_list=[]
        result=emoji_str
        #先找位置
        for m in co.finditer(emoji_str):
            pos_list.append((m.start(),m.end()))
        #根据位置拼接替换
        for pos in range(len(pos_list)):
            if pos==0:
                result=emoji_str[0:pos_list[0][0]]
            else:
                result=result+emoji_str[pos_list[pos-1][1]:pos_list[pos][0]]
            result = result +eval(emoji_str[pos_list[pos][0]:pos_list[pos][1]])
            if pos==len(pos_list)-1:
                result=result+emoji_str[pos_list[pos][1]:len(emoji_str)]
        return result


# print urllib.quote('http://skihelp.cn/b/wx/asb?t=infoauth.html?cb=8afcb239990b7d99ad01e2f9044f1e09')
# print int(time.time())

# mydict = dict()
# mydict['noncestr'] = 'a817def4b93a4e439b90b1be122992cd'
# mydict['jsapi_ticket'] = 'kgt8ON7yVITDhtdwci0qeTkfCiEgL8-LsAub_8j6XhInnyFEjq5dxbaO3lPqU9VIKMZpHOvdx16AauOCN-Lr3g'
# mydict['timestamp'] = '1480049549'
# mydict['url'] = 'http://skihelp.cn/teaminfo.html?tid=52e15c24560e4bb8af3953e2c043d04d&id=o2pJcvz6msVs08t49EU8zsLjAaXo'
# #
# print U.sign_sha1(mydict)
# print "i love %(python)s " % {'python':'ddd','p1':'eee'}
#print datetime.datetime.now() - datetime.timedelta(hours=24)
# print U.gen_refund_id()
# print '%0.0f元' % 200.00000