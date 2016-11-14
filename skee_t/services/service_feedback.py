#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import User, Feedback
from skee_t.services import BaseService
from skee_t.services.service_validator import FeedbackCreateValidator

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class FeedbackService(BaseService):
    """

    """

    def __init__(self):
        pass

    @FeedbackCreateValidator
    def create_feedback(self, dict_args={}):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        feedback = Feedback(user_uuid=dict_args.get('userId'),
                            contact=dict_args.get('contact'),
                            content=dict_args.get('content'),
                            creator=dict_args.get('userId'),
                            updater=dict_args.get('userId')
                    )

        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            session.add(feedback)
            session.commit()
        except Exception as e:
            LOG.exception("Create user information error.")
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def list_feedback(self, user_id=None, phone_no=None):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            u_query = session.query(User)
            if user_id:
                u_query = u_query.filter(User.uuid == user_id)
            if phone_no:
                u_query = u_query.filter(User.phone_no == phone_no)
            return u_query.one()
        except NoResultFound as e:
            LOG.exception("get_user_auth_info error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}