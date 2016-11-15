# -*- coding: utf-8 -*-
# filename: basic.py
import datetime
import logging
import time

from skee_t.Singleton import Singleton
from skee_t.db.models import WxAccessToken
from skee_t.utils.u import U
from skee_t.wx.proxy.accessToken import WxAccTokenProxy
from skee_t.wx.services.accessToken import wxAccessTokenService

LOG = logging.getLogger(__name__)


class WxBasic(Singleton):
    __accessToken = None
    __expireTime = None
    uuid = None
    state = 0

    def __real_get_access_token(self):
        if self.state == 2:
            time.sleep(2)
            if self.__accessToken:
                return
        self.state = 2 # 处理中
        accToken = WxAccTokenProxy().get_access_token_remote()
        self.__accessToken = accToken.access_token
        self.__expireTime = datetime.datetime.now() + datetime.timedelta(seconds=(accToken.expires_in-200))
        self.uuid = U.gen_uuid()
        wxAccessTokenService().add(self.uuid, self.__accessToken, accToken.expires_in)
        self.state = 1 # 可用
        LOG.info('set self and save table uuid: %s:' % self.uuid)

    def __db_get_access_token(self):
        queryRst = wxAccessTokenService().query(1)
        LOG.info('post-request-db-rst: %s' % queryRst)
        if isinstance(queryRst, WxAccessToken):
            self.__expireTime = queryRst.entry_time + datetime.timedelta(seconds=(queryRst.expires_in-200))
            if self.__expireTime > datetime.datetime.now():
                self.__accessToken = queryRst.access_token
                self.uuid = queryRst.uuid
            else:
                wxAccessTokenService().update(queryRst.uuid, 0)

    def get_access_token(self):
        if not self.__accessToken:
            self.__db_get_access_token()
        if not self.__accessToken:
            self.__real_get_access_token()
        if self.__accessToken and self.__expireTime \
                and self.__expireTime < datetime.datetime.now():
            wxAccessTokenService().update(self.uuid, 0)
            self.__real_get_access_token()
        return self.__accessToken