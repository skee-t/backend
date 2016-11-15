# -*- coding: utf-8 -*-
# filename: basic.py
import json
import logging
import urllib

from skee_t.conf import CONF
from skee_t.db.models import WxAccessToken

LOG = logging.getLogger(__name__)


class WxAccTokenProxy(object):

    def get_access_token_remote(self):
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (CONF.wxp.appid, CONF.wxp.appsecret))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        LOG.info('post-request-weixin-rst: %s' % urlResp)
        return WxAccessToken(access_token=urlResp['access_token'],
                             expires_in=urlResp['expires_in'])

