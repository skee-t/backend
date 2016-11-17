#! -*- coding: UTF-8 -*-
import logging

from skee_t.db import DbEngine

__author__ = 'rensikun'

LOG = logging.getLogger(__name__)


class BaseService(object):
    """
    A class which represents the generic attributes and methods for all service classes.
    """
    def create(self, obj):
        """
        创建对象方法
        :param obj
        :return:
        """
        session = None
        try:
            session = DbEngine.get_session_simple()
            session.add(obj)
            session.commit()
        except Exception as e:
            LOG.exception("Create %s error." % type(obj))
            if session is not None:
                session.rollback()