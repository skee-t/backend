#! -*- coding: UTF-8 -*-

import logging
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import User, UserLevelTran, UserEvent, Level
from skee_t.services import BaseService
from skee_t.services.service_validator import UserCreateValidator
from skee_t.utils.u import U

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
        user = User(uuid=U.gen_uuid(),
                    open_id=dict_args.get('openId'),
                    phone_no=dict_args.get('phoneNo'),
                    name=dict_args.get('name'),
                    real_name=dict_args.get('realName'),
                    head_image_path=dict_args.get('headImagePath'),
                    sex=dict_args.get('sex'),
                    country=dict_args.get('country'),
                    province=dict_args.get('province'),
                    city=dict_args.get('city'),
                    ski_age=dict_args.get('skiAge'),
                    ski_level=dict_args.get('skiLevel'),
                    ski_type=dict_args.get('skiType'),
                    history=dict_args.get('history'),
                    )
        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
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

    def get_user(self, open_id = None, user_id=None, phone_no=None):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            engine = DbEngine.get_single()
            session = engine.get_session(autocommit=False, expire_on_commit=True)

            u_query = session.query(User)
            if open_id:
                u_query = u_query.filter(User.open_id == open_id)
            if user_id:
                u_query = u_query.filter(User.uuid == user_id)
            if phone_no:
                u_query = u_query.filter(User.phone_no == phone_no)
            return u_query.one()
        except NoResultFound as e:
            LOG.exception("get_user_auth_info error.")
            rst_code = 100000
            rst_desc = '用户不存在'
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def get_level(self, type = None, level=None):
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
            return session.query(Level)\
                .filter(Level.type == type).filter(Level.level == level).one()
        except NoResultFound as e:
            LOG.exception("get_level error.")
            rst_code = 100000
            rst_desc = '等级信息不存在'
        except (TypeError, Exception) as e:
            LOG.exception("List level information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def level_update(self, activity_id, members):
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
            users = session.query(User).filter(User.uuid.in_(members)).all()

            # 批量增加用户等级变化信息
            user_level_trans_dict = \
                [{'uuid':U.gen_uuid(), 'user_uuid':item.uuid,'activity_uuid':activity_id,
                  'org_level':item.ski_level, 'level':item.ski_level+1, 'entry_time': datetime.now()}
                                    for item in users]
            session.execute(UserLevelTran.__table__.insert(), user_level_trans_dict)

            # 批量修改用户等级
            session.query(User).filter(User.uuid.in_(members)).update(
                {User.ski_level:User.ski_level+1, User.update_time:datetime.now()},
                synchronize_session=False
                )

            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def add_user_event(self, open_id, target_id):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        userEvent = UserEvent(uuid=U.gen_uuid(),
                              open_id=open_id,
                              target_id=target_id,
                    )
        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            # Save current location and job information
            session.add(userEvent)
            session.commit()
        except Exception as e:
            LOG.exception("Create userEvent error.")
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}