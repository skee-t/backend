#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import now

from skee_t.db import DbEngine
from skee_t.db.models import SpToken, SpCount
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SpService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_sp(self, sp_token, sp_count_flag):
        """
        创建活动
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """

        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            session.add(sp_token)
            if sp_count_flag == 0: # 不存在,新增加sp_count
                session.add(SpCount(phone_no=sp_token.__getattribute__('phone_no')))
            elif sp_count_flag == 1: # 有效时间内,需times+1
                session.query(SpCount)\
                    .filter(SpCount.phone_no == sp_token.__getattribute__('phone_no'))\
                    .update({SpCount.times:SpCount.times+1, SpCount.last_time:now()}, synchronize_session=False)
            elif sp_count_flag == 2: # 已超过1小时,属过期,需重置times=1
                session.query(SpCount) \
                    .filter(SpCount.phone_no == sp_token.__getattribute__('phone_no')) \
                    .update({SpCount.times:1, SpCount.last_time:now()}, synchronize_session=False)
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
    def select_sp_count(self, phone_no):
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            return session.query(SpCount).filter(SpCount.phone_no == phone_no).one()
        except NoResultFound:
            LOG.info("no-found-sp_count %s" % phone_no)
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List sp count error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message

        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def select_sp_token(self, phone_no, token):
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            return session.query(SpToken).filter(SpToken.phone_no == phone_no).filter(SpToken.token == token).one()
        except NoResultFound:
            LOG.info("no-found-sp_token %s" % phone_no)
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List sp count error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def update_sp(self, phone_no, token, state=None):
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            # 更新sp_token
            session.query(SpToken) \
                .filter(SpToken.token == token).filter(SpToken.phone_no == phone_no) \
                .update({SpToken.state:state,
                         SpToken.verify_count: SpToken.verify_count+1,
                         SpToken.last_time:now()},
                        synchronize_session=False)

            # 验证通过,清空sp_count
            if state == 1:
                session.query(SpCount) \
                    .filter(SpCount.phone_no == phone_no) \
                    .update({SpCount.times:0, SpCount.last_time:now()},
                            synchronize_session=False)
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("List sp count error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}
