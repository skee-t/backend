#! -*- coding: UTF-8 -*-

import logging
import uuid

from skee_t.db import DbEngine
from skee_t.db.models import Activity, User
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class ActivityService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_activity_teach(self, dict_args={}):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        activity = Activity(  uuid=str(uuid.uuid4()),
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
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            session.add(activity)
            session.commit()
        except Exception as e:
            LOG.exception("Create SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}

    # @SkiResortListValidator
    def list_skiResort_activity(self, skiResort_uuid = None, type=None, leader_id = None, page_index = 1):
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
            query_sr = session.query(User.uuid.label('leader_id'), User.name.label('leader_name'),
                                     User.head_image_path.label('leader_head_image_path'),
                                     Activity.uuid.label('id'), Activity.title, Activity.type, Activity.state,
                                     Activity.fee, Activity.period, Activity.meeting_time, Activity.contact)\
                .filter(User.uuid == Activity.creator)
            if skiResort_uuid:
                query_sr = query_sr.filter(Activity.ski_resort_uuid == skiResort_uuid)
            if type:
                query_sr = query_sr.filter(Activity.type == type)
            if leader_id:
                query_sr = query_sr.filter(Activity.creator == leader_id)

            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}
