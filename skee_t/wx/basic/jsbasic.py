# -*- coding: utf-8 -*-
# filename: basic.py
import datetime
import logging
import time

from skee_t.Singleton import Singleton
from skee_t.db.models import WxJSAPIToken
from skee_t.utils.u import U
from skee_t.wx.basic.basic import WxBasic
from skee_t.wx.proxy.accessToken import WxAccTokenProxy
from skee_t.wx.services.jsapiToken import wxJsapiTokenService

LOG = logging.getLogger(__name__)


class WxJSBasic(Singleton):
    __ticket = None
    __expireTime = None
    uuid = None
    state = 0

    def __real_get_jsapi_ticket(self):
        if self.state == 2:
            time.sleep(2)
            if self.__ticket:
                return
        self.state = 2 # 处理中
        acc_token = WxBasic().get_access_token()
        jsapiTicket = WxAccTokenProxy().get_jsapi_ticket_remote(acc_token)
        self.__ticket = jsapiTicket.ticket
        self.__expireTime = datetime.datetime.now() + datetime.timedelta(seconds=(jsapiTicket.expires_in-200))
        self.uuid = U.gen_uuid()
        wxJsapiTokenService().add(self.uuid, self.__ticket, jsapiTicket.expires_in)
        self.state = 1 # 可用
        LOG.info('set self and save table uuid: %s:' % self.uuid)

    def __db_get_jsapi_ticket(self):
        queryRst = wxJsapiTokenService().query(1)
        LOG.info('post-request-db-rst: %s' % queryRst)
        if isinstance(queryRst, WxJSAPIToken):
            self.__expireTime = queryRst.entry_time + datetime.timedelta(seconds=(queryRst.expires_in-200))
            if self.__expireTime > datetime.datetime.now():
                self.__ticket = queryRst.ticket
                self.uuid = queryRst.uuid
            else:
                wxJsapiTokenService().update(queryRst.uuid, 0)

    def get_jsapi_ticket(self):
        if not self.__ticket:
            self.__db_get_jsapi_ticket()
        if not self.__ticket:
            self.__real_get_jsapi_ticket()
        if self.__ticket and self.__expireTime \
                and self.__expireTime < datetime.datetime.now():
            wxJsapiTokenService().update(self.uuid, 0)
            self.__real_get_jsapi_ticket()
        return self.__ticket