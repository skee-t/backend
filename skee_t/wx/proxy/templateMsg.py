# -*- coding: utf-8 -*-
# filename: basic.py
import json
import logging
import urllib

import requests

from skee_t.conf import CONF
from skee_t.db.models import WxAccessToken, WxJSAPIToken

LOG = logging.getLogger(__name__)


class WxTempMsgProxy(object):

    def send(self, acc_token, msg):
        postUrl = ("https://api.weixin.qq.com/cgi-bin/message/template/send?"
                   "access_token=%s" % acc_token)
        LOG.info('send %s' % msg)
        r = requests.post (postUrl, data = msg)
        LOG.info('rece %s' % r.content)
        urlResp = json.loads(r.content)
        return urlResp

