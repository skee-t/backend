#! -*- coding: UTF-8 -*-

import datetime
import logging

from sqlalchemy import exists
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.elements import and_

# from sqlalchemy.sql.expression import func, text
from sqlalchemy.sql.functions import now

from skee_t.db import DbEngine
from skee_t.db.models import Activity, User, ActivityMember, Msg
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class TaskService(BaseService):
    """

    """

    def __init__(self):
        pass

    def change_activity(self, src_states, dst_state):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            count = session.query(Activity).filter(Activity.state.in_(src_states))\
                .filter(Activity.meeting_time <= now()) \
                .filter(Activity.type != 0) \
                .update({Activity.state: dst_state,
                        Activity.updater:'task',
                        Activity.update_time: now()}
                       ,synchronize_session=False)
            session.commit()
            LOG.info("change_activity count:%d" % count)
        except Exception as e:
            LOG.exception("start_activity error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def change_activity_finish(self):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            count = session.execute('update activitys set state=3,updater=:updater,update_time=now() '
                                    'where date_add(meeting_time, interval period hour) <= now() and state=2',
                            {'updater': 'task'});
            session.commit()
            LOG.info("change_activity_finish count:%d" % count.rowcount)
        except Exception as e:
            LOG.exception("change_activity_finish error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def list_act_wait_pro(self, type=None, page_index = None):
        """
        教学活动结束4小时内,推送评级提醒
        :param
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            query_sr = session.query(User.uuid.label('leader_id'), User.name.label('leader_name'),
                                     Activity.uuid.label('activity_id'), User.phone_no) \
                .filter(User.uuid == Activity.creator)\
                .filter(Activity.state == 3) \
                .filter(Activity.update_time >= datetime.datetime.now() - datetime.timedelta(hours=4)) \
                .filter(Activity.type == type) \
                .filter(exists().where(
                    and_(ActivityMember.activity_uuid == Activity.uuid, ActivityMember.state == 2))) \
                .filter(~exists().where(
                    and_(Msg.target_id == User.uuid, Msg.activity_id == Activity.uuid, Msg.type == 5))) \
                .order_by(Activity.meeting_time.desc())
            return query_sr.offset((int(page_index)-1)*20).limit(int(page_index)*20).all()
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
    def list_member_wait_comment(self, type=None, page_index = None):
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
            query_sr = session.query(User.uuid.label('member_id'), User.name.label('member_name'),
                                     User.phone_no.label('phone_no'),
                                     Activity.uuid.label('activity_id')) \
                .filter(User.uuid == ActivityMember.user_uuid) \
                .filter(ActivityMember.activity_uuid == Activity.uuid) \
                .filter(ActivityMember.state.in_([2, 3])) \
                .filter(Activity.state.in_([3,4])) \
                .filter(Activity.update_time >= datetime.datetime.now() - datetime.timedelta(hours=8)) \
                .filter(Activity.type == type) \
                .filter(~exists().where(
                    and_(Msg.target_id == User.uuid, Msg.activity_id == Activity.uuid, Msg.type == 3))) \
                .order_by(Activity.meeting_time.desc())
            return query_sr.offset((int(page_index)-1)*50).limit(int(page_index)*50).all()
        except NoResultFound as e:
            LOG.exception("List activity information error.")
            return {'rst_code': 100000, 'rst_desc': '未找到活动'}
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}
