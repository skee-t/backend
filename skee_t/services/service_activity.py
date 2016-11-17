#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy import exists
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import now

from skee_t.db import DbEngine
from skee_t.db.models import Activity, User, SkiResort, ActivityMember, UserEvent
from skee_t.services import BaseService
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class ActivityService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_activity(self, dict_args={}):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        uuid_str = U.gen_uuid()
        activity = Activity(  uuid=uuid_str,
                              type=dict_args.get('type'),
                              title=dict_args.get('title'),
                              ski_resort_uuid=dict_args.get('skiResortId'),
                              contact=dict_args.get('contact'),
                              level_limit=dict_args.get('levelLimit'),
                              venue=dict_args.get('venue'),
                              meeting_time=dict_args.get('meetingTime'),
                              quota=dict_args.get('quota'),
                              fee=dict_args.get('fee'),
                              period=dict_args.get('period'),
                              notice=dict_args.get('notice'),
                              creator=dict_args.get('creator'),
                              updater=dict_args.get('creator'),
                    )

        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            session.add(activity)
            session.commit()
        except Exception as e:
            LOG.exception("Create SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc, 'uuid':uuid_str}

    # @SkiResortListValidator
    def list_skiResort_activity(self, skiResort_uuid = None, type=None, leader_id = None,
                                member_id_un_estimate = None, member_id_join = None, user_id_join = None,
                                teach_id = None, page_index = None):
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
            sbq_join_count = session.query(func.count(ActivityMember.activity_uuid))\
                .filter(Activity.uuid == ActivityMember.activity_uuid).correlate(Activity).as_scalar()

            sbq_interest_count = session.query(func.count(UserEvent.open_id.distinct())) \
                .filter(UserEvent.target_id == Activity.uuid).correlate(Activity).as_scalar()

            query_sr = session.query(User.uuid.label('leader_id'), User.name.label('leader_name'),
                                     User.head_image_path.label('leader_head_image_path'),
                                     Activity.uuid.label('id'), Activity.title, Activity.type, Activity.state,
                                     Activity.fee, Activity.period, Activity.meeting_time, Activity.contact,
                                     Activity.estimate,
                                     sbq_join_count.label('join_count'),sbq_interest_count.label('interest_count')) \
                .filter(User.uuid == Activity.creator)
            if skiResort_uuid:
                query_sr = query_sr.filter(Activity.ski_resort_uuid == skiResort_uuid)
            if type:
                query_sr = query_sr.filter(Activity.type == type)
            if leader_id:
                query_sr = query_sr.filter(Activity.creator == leader_id)
            if teach_id:
                query_sr = query_sr.filter(Activity.uuid == teach_id)
                return query_sr.one()
            if member_id_un_estimate:
                # 用户参与的已经结束的未评价活动(非领队)
                # 活动状态为3-已结束 4-学员已晋级
                query_sr = query_sr\
                    .filter(exists().where(
                                and_(ActivityMember.activity_uuid == Activity.uuid,
                                     ActivityMember.user_uuid == member_id_un_estimate,
                                     ActivityMember.estimate_score == 0)))\
                    .filter(Activity.state >= 3)\
                    .filter(Activity.creator != member_id_un_estimate)
            if member_id_join:
                # 用户参与的活动(非领队)
                query_sr = query_sr \
                    .filter(exists().
                            where(and_(ActivityMember.user_uuid == member_id_join,
                                       ActivityMember.activity_uuid == Activity.uuid))) \
                    .filter(Activity.creator != member_id_join)\
                    .order_by(Activity.meeting_time.desc())
            else:
                query_sr = query_sr.order_by(Activity.create_time.desc())

            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except NoResultFound as e:
            LOG.exception("List activity information error.")
            return {'rst_code': 100000, 'rst_desc': '未找到活动'}
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def get_activity_his(self, user_id_join, page_index):
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
            query_sr = session.query(Activity.uuid.label('id'), Activity.title, Activity.type, Activity.state,
                                     Activity.meeting_time, Activity.ski_resort_uuid.label('ski_resort_id'),
                                     SkiResort.name.label('ski_resort_name')
                                     ) \
                .filter(SkiResort.uuid == Activity.ski_resort_uuid)
            if user_id_join:
                # 用户参与的活动(包含领队)
                query_sr = query_sr \
                    .filter(exists().
                            where(and_(ActivityMember.user_uuid == user_id_join,
                                       ActivityMember.activity_uuid == Activity.uuid))) \
                    .order_by(Activity.meeting_time.desc())
            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except NoResultFound as e:
            LOG.exception("List activity information error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def get_activity(self, activity_id, type, leader_id=None, state = None):
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
            query_sr = session.query(Activity.uuid.label('id'), Activity.title, Activity.type, Activity.state,
                                     Activity.level_limit, Activity.meeting_time, Activity.venue, Activity.period,
                                     Activity.fee, Activity.quota, Activity.notice,
                                     Activity.ski_resort_uuid.label('ski_resort_id'),
                                     SkiResort.name.label('ski_resort_name'),SkiResort.trail_pic,
                                     User.uuid.label('leader_id'), User.name.label('leader_name'), User.phone_no.label('leader_phone'), Activity.contact.label('leader_contact')
                                     ) \
                .filter(User.uuid == Activity.creator) \
                .filter(SkiResort.uuid == Activity.ski_resort_uuid) \
                .filter(Activity.type == type) \
                .filter(Activity.uuid == activity_id)
            if state:
                query_sr = query_sr.filter(Activity.state == state)
            if leader_id:
                query_sr = query_sr.filter(User.uuid == leader_id)
            return query_sr.one()
        except NoResultFound as e:
            LOG.exception("List activity information error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def detail_teach_team(self, teach_id):
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
            query_sr = session.query(User.uuid.label('leader_id'), User.name.label('leader_name'),
                                     User.head_image_path.label('leader_head_image_path'),
                                     Activity.uuid.label('id'), Activity.title, Activity.type, Activity.state,
                                     Activity.fee, Activity.period, Activity.meeting_time, Activity.contact,
                                     Activity.notice) \
                .filter(User.uuid == Activity.creator) \
                .filter(User.uuid == Activity.creator) \
                .filter(Activity.type == 1) \
                .filter(Activity.uuid == teach_id)
            return query_sr.one()
        except NoResultFound as e:
            LOG.exception("detail_teach_team error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def update(self, teach_id, org_state, new_state, updater):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        try:
            session = DbEngine.get_session_simple()
            session.query(Activity) \
                .filter(Activity.uuid == teach_id).filter(Activity.state == org_state) \
                .update({Activity.state:new_state,
                         Activity.updater:updater,
                         Activity.update_time:now()}
                        ,synchronize_session=False
                        )
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            return {'rst_code': 999999, 'rst_desc': e.message}