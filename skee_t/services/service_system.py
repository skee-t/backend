#! -*- coding: UTF-8 -*-

import logging

from skee_t.db import DbEngine
from skee_t.db.models import Property
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SysService(BaseService):
    """

    """

    def __init__(self):
        pass

    @classmethod
    def getByKey(self, key):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        try:
            session = DbEngine.get_session_simple()
            return session.query(Property).filter(Property.key==key)\
                .order_by(Property.create_time.desc()).first()
        except Exception as e:
            LOG.exception("get Property error.")
            rst_code = '999999'
            rst_desc = e.message
            return {'rst_code':rst_code, 'rst_desc':rst_desc}
