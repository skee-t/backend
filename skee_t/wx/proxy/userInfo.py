# -*- coding: utf-8 -*-
# filename: basic.py
import json
import logging
import urllib

LOG = logging.getLogger(__name__)


class UserInfoProxy(object):

    def get(self, accesstoken, openid):
        postUrl = ("https://api.weixin.qq.com/cgi-bin/user/info?"
                   "access_token=%s&openid=%s&lang=zh_CN" % (accesstoken, openid))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        LOG.info('post-request-weixin-rst: %s' % urlResp)
        return urlResp

