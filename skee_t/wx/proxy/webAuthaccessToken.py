# -*- coding: utf-8 -*-
# filename: basic.py
import json
import logging
import urllib

from skee_t.conf import CONF
from skee_t.db.models import WxWebAccessToken

LOG = logging.getLogger(__name__)


class WxOpenIdProxy(object):
    @staticmethod
    def get_open_id(code):
        # https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
        postUrl = ("https://api.weixin.qq.com/sns/oauth2/access_token?grant_type=authorization_code"
                   "&appid=%s&secret=%s&code=%s" % (CONF.wxp.appid, CONF.wxp.appsecret, code))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        LOG.info('get_web_access_token_remote-rst: %s' % urlResp)
        return WxWebAccessToken(access_token=urlResp['access_token'],
                                expires_in=urlResp['expires_in'],
                                scope=urlResp['scope'],
                                open_id=urlResp['openid'])
