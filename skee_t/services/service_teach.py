#! -*- coding: UTF-8 -*-

import logging
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import now, func

from skee_t.db import DbEngine
from skee_t.db.models import User, ActivityMember, Activity
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
        rst_code = 0
        rst_desc = 'success'
        session = DbEngine.get_session_simple()
        # 0 检查是否有退出记录
        try:
            activityMember = session.query(ActivityMember) \
                            .filter(ActivityMember.activity_uuid==activity_uuid,
                            ActivityMember.user_uuid==user_uuid).one()
            if activityMember.state == -2:
                session.query(ActivityMember) \
                    .filter(ActivityMember.activity_uuid==activity_uuid,
                            ActivityMember.user_uuid==user_uuid)\
                    .update({ActivityMember.state:0, ActivityMember.update_time:datetime.now()},
                            synchronize_session=False)
                session.commit()
            return {'rst_code':rst_code, 'rst_desc':rst_desc}
        except NoResultFound as e:
            LOG.info("activityMember not exists.")
        except Exception as e:
            LOG.exception("Create SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc}

        # 增加活动成员信息
        try:
            activityMember = ActivityMember(
                activity_uuid = activity_uuid,
                user_uuid = user_uuid,
                state = state,
            )
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
            session = DbEngine.get_session_simple()
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

            return query_sr.order_by(ActivityMember.state.desc(), ActivityMember.create_time.asc()).all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def member_count(self, teach_id, states):
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
            return session.query(func.count(ActivityMember.user_uuid).label('member_count')) \
                .filter(ActivityMember.activity_uuid == teach_id).filter(ActivityMember.state.in_(states)).one()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def member_update(self, teach_id, members, src_state, state, session_com = None):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        try:
            if not session_com:
                session = DbEngine.get_session_simple()
            else:
                session = session_com
            session.query(ActivityMember) \
                .filter(ActivityMember.activity_uuid == teach_id,ActivityMember.state == src_state)\
                .filter(ActivityMember.user_uuid.in_(members)) \
                .update({ActivityMember.state:state,
                         ActivityMember.update_time:now()}
                        ,synchronize_session=False
                        )
            if not session_com:
                session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            return {'rst_code': 999999, 'rst_desc': e.message}

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
            session = DbEngine.get_session_simple()
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
    def list_estimate(self, teach_id = None, teacher_id = None, user_id = None, page_index = None):
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
            est_query = session.query(ActivityMember.user_uuid.label('user_id'),
                                      User.name.label('user_name'),
                                      ActivityMember.estimate_type.label('type'),
                                      ActivityMember.estimate_score.label('score'),
                                      ActivityMember.estimate_content.label('content'),
                                      ActivityMember.update_time.label('est_time'))\
                .filter(ActivityMember.user_uuid == User.uuid)\
                .filter(ActivityMember.estimate_score != 0) \
                .filter(Activity.state > 2)\
                .filter(ActivityMember.activity_uuid == Activity.uuid)
            if teach_id:
                est_query = est_query.filter(ActivityMember.activity_uuid == teach_id)
            if user_id:
                est_query = est_query.filter(User.uuid == user_id)
            if teacher_id:
                est_query = est_query.filter(Activity.creator == teacher_id)
            # 统一按照更新时间倒序排列
            est_query = est_query.order_by(ActivityMember.update_time.desc())
            if page_index:
                est_query = est_query.offset((int(page_index)-1)*5).limit(int(page_index)*5)
            return est_query.all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # 获取教练的教学次数
    def teach_count(self, teacher_id):
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
            return session.query(func.count(Activity.uuid).label('teach_count')) \
                .filter(Activity.creator == teacher_id).filter(Activity.state > 2).one()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}