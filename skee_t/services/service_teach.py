#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.sql.functions import now

from skee_t.db import DbEngine
from skee_t.db.models import User, ActivityMember
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class MemberService(BaseService):
    """

    """

    def __init__(self):
        pass

    def add_member(self, activity_uuid, user_uuid, state=0):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        activityMember = ActivityMember(
                                        activity_uuid = activity_uuid,
                                        user_uuid = user_uuid,
                                        state = state,
                                    )

        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            session.add(activityMember)
            session.commit()
        except Exception as e:
            LOG.exception("Create SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}

    # @SkiResortListValidator
    def list_member(self, teach_id, state, leader_id = None):
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
            query_sr = session.query(ActivityMember.user_uuid.label('id'), ActivityMember.state,
                                     User.head_image_path, User.name, User.ski_level,) \
                .filter(ActivityMember.user_uuid == User.uuid) \
                .filter(ActivityMember.activity_uuid == teach_id)
            if isinstance(state, int):
                query_sr = query_sr.filter(ActivityMember.state == state)
            elif isinstance(state, list):
                query_sr = query_sr.filter(ActivityMember.state.in_(state))

            # 排除领队
            if leader_id:
                query_sr = query_sr.filter(ActivityMember.user_uuid != leader_id)

            return query_sr.all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def member_update(self, teach_id, members, state):
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
            session.query(ActivityMember) \
                .filter(ActivityMember.activity_uuid == teach_id).filter(ActivityMember.user_uuid.in_(members)) \
                .update({ActivityMember.state:state,
                         ActivityMember.update_time:now()}
                        ,synchronize_session=False
                        )
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def member_estimate(self, dict_args={}):
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
            session.query(ActivityMember) \
                .filter(ActivityMember.activity_uuid == dict_args.get('teachId'))\
                .filter(ActivityMember.user_uuid == dict_args.get('userId')) \
                .update({ActivityMember.estimate_type:dict_args.get('type'),
                         ActivityMember.estimate_score:dict_args.get('score'),
                         ActivityMember.estimate_content:dict_args.get('content'),
                         ActivityMember.update_time:now()}
                        ,synchronize_session=False
                        )
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def list_estimate(self, teach_id):
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
            return session.query(ActivityMember.user_uuid.label('user_id'), User.name.label('user_name'),
                                 ActivityMember.estimate_type.label('type'),
                                 ActivityMember.estimate_score.label('score'),
                                 ActivityMember.estimate_content.label('content'))\
                .filter(ActivityMember.user_uuid == User.uuid)\
                .filter(ActivityMember.activity_uuid == teach_id)\
                .filter(ActivityMember.estimate_score != 0)\
                .all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}