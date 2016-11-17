#! -*- coding: UTF-8 -*-

import logging
from datetime import datetime

from skee_t.db import DbEngine
from skee_t.db.models import User, Msg, Activity
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class MsgService(BaseService):
    """

    """

    def __init__(self):
        pass

    def getList(self, target_user_id, page_index):
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
            query_sr = session.query(Msg.uuid.label('id'), Msg.type, Msg.create_time,
                                     User.name.label('src_user_name'),
                                     User.head_image_path.label('src_head_image_path'),
                                     Activity.title.label('activity_title'),
                                     Activity.uuid.label('activity_id')) \
                .filter(Msg.source_id == User.uuid) \
                .filter(Msg.activity_id == Activity.uuid) \
                .filter(Msg.target_id == target_user_id)\
                .order_by(Msg.create_time.desc())
            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except Exception as e:
            LOG.exception("List msg information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update(self, uuid, state):
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
            session.query(Msg)\
                .filter(Msg.uuid == uuid).update(
                {Msg.state:state, Msg.update_time:datetime.now()},
                synchronize_session=False)
        except (TypeError, Exception) as e:
            LOG.exception("List level information error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}
