#! -*- coding: UTF-8 -*-

import json
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
        user = User(uuid=uuid.uuid4(),
                    name=dict_args.get('name'),
                    real_name=dict_args.get('real_name'),
                    image_path=dict_args.get(''),
                    sex=dict_args.get('sex'),
                    age=dict_args.get('age'),
                    level=dict_args.get('level'),
                    contact=dict_args.get('contact'),
                    appliance=dict_args.get('appliance'),
                    history=dict_args.get('history'),
                    )
        session = None
        rst_status = False
        try:
            engine = DbEngine().get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            # Save current location and job information
            session.add(user)
            session.commit()
            rst_status = True
        except Exception as e:
            LOG.error("Create user information error.", e)
            if session is not None:
                session.rollback()
        return rst_status
