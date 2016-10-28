#! -*- coding: UTF-8 -*-

import logging
import uuid

from skee_t.db import DbEngine
from skee_t.db.models import User
from skee_t.services import BaseService
from skee_t.services.service_validator import UserCreateValidator

__author__ = 'pluto'


LOG = logging.getLogger(__name__)


class UserService(BaseService):
    """

    """

    def __init__(self):
        pass

    @UserCreateValidator
    def create_user(self, dict_args={}):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        user = User(uuid=str(uuid.uuid4()),
                    phone_no=dict_args.get('phoneNo'),
                    name=dict_args.get('name'),
                    real_name=dict_args.get('realName'),
                    head_image_path=dict_args.get('headImagePath'),
                    sex=dict_args.get('sex'),
                    ski_age=dict_args.get('skiAge'),
                    ski_level=dict_args.get('skiLevel'),
                    ski_type=dict_args.get('skiType'),
                    history=dict_args.get('history'),
                    )
        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            # Save current location and job information
            session.add(user)
            session.commit()
        except Exception as e:
            LOG.exception("Create user information error.")
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def get_user_auth_info(self, user_id=None, phone_no=None):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            u_query = session.query(User)
            if user_id:
                u_query = u_query.filter(User.uuid == user_id)
            if phone_no:
                u_query = u_query.filter(User.phone_no == phone_no)
            return u_query.one()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}
