#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import and_

from skee_t.db import DbEngine
from skee_t.db.models import SkiResort, TeachingFee, ActivityMember, Activity, UserEvent
from skee_t.services import BaseService
from skee_t.services.service_validator import SkiResortCreateValidator
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SkiResortService(BaseService):
    """

    """

    def __init__(self):
        pass

    @SkiResortCreateValidator
    def create_skiResort(self, dict_args={}):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        skiResort = SkiResort(uuid=U.gen_uuid(),
                              name=dict_args.get('name'),
                              city=dict_args.get('city'),
                              address=dict_args.get('address'),
                              spec_pic=dict_args.get('specPic'),
                              trail_pic=dict_args.get('trailPic'),
                              contact=dict_args.get('contact'),
                              creator=dict_args.get('creator'),
                              updater=dict_args.get('creator'),
                    )

        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            session.add(skiResort)
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
    def list_skiResort(self, uuid = None, city = None, page_index = 1):
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
            query_sr = session.query(SkiResort.uuid.label('id'), SkiResort.name, SkiResort.city,
                                     SkiResort.address, SkiResort.spec_pic, SkiResort.trail_pic, SkiResort.has_bus)

            if uuid:
                return query_sr.filter_by(uuid=uuid).one()
            elif city:
                query_sr = query_sr.filter_by(city=city)
            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}


    # @SkiResortListValidator
    def list_skiResort_with_count(self, uuid = None, city = None, page_index = 1):
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

            sbq_join_count = session.query(func.count(ActivityMember.activity_uuid)) \
                .filter(Activity.uuid == ActivityMember.activity_uuid) \
                .filter(Activity.ski_resort_uuid == SkiResort.uuid).correlate(SkiResort).as_scalar()

            sbq_interest_count = session.query(func.count(UserEvent.open_id.distinct())) \
                .filter(UserEvent.target_id == Activity.uuid) \
                .filter(Activity.ski_resort_uuid == SkiResort.uuid).correlate(SkiResort).as_scalar()

            query_sr = session.query(SkiResort.uuid.label('id'), SkiResort.name, SkiResort.city,
                                     SkiResort.address, SkiResort.spec_pic, SkiResort.trail_pic, SkiResort.has_bus,
                                     sbq_join_count.label('join_count'),sbq_interest_count.label('interest_count'))

            if uuid:
                return query_sr.filter_by(uuid=uuid).one()
            elif city:
                query_sr = query_sr.filter_by(city=city)
            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def list_skiResort_often(self, user_id, page_index):
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

            sbq_join_count = session.query(func.count(ActivityMember.activity_uuid)) \
                .filter(Activity.uuid == ActivityMember.activity_uuid) \
                .filter(Activity.ski_resort_uuid == SkiResort.uuid).correlate(SkiResort).as_scalar()

            sbq_interest_count = session.query(func.count(UserEvent.open_id.distinct())) \
                .filter(UserEvent.target_id == Activity.uuid) \
                .filter(Activity.ski_resort_uuid == SkiResort.uuid).correlate(SkiResort).as_scalar()

            query_sr = session.query(func.max(Activity.create_time),SkiResort.uuid.label('id'), SkiResort.name, SkiResort.city,
                                     SkiResort.address, SkiResort.spec_pic, SkiResort.trail_pic, SkiResort.has_bus,
                                     sbq_join_count.label('join_count'),sbq_interest_count.label('interest_count'))

            # 用户参与的活动
            query_sr = query_sr \
                .filter(SkiResort.uuid == Activity.ski_resort_uuid) \
                .filter(exists().where(and_(ActivityMember.user_uuid == user_id,
                                            ActivityMember.activity_uuid == Activity.uuid))) \
                .order_by(func.max(Activity.create_time).desc())

            return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    # @SkiResortListValidator
    def list_skiResort_simple(self, ski_type, skiResort_id, page_index):
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
            query_sr = session.query(SkiResort.uuid.label('id'), SkiResort.name, SkiResort.address, SkiResort.city,
                                     TeachingFee.fee_desc.label('teaching_fee'))\
                .outerjoin(TeachingFee, TeachingFee.ski_resort_uuid == SkiResort.uuid)\
                .filter(or_(TeachingFee.ski_type == None, TeachingFee.ski_type == ski_type))
            if skiResort_id:
                query_sr = query_sr.filter(SkiResort.uuid == skiResort_id)
            else:
                query_sr = query_sr.order_by(SkiResort.city,SkiResort.name)
            if page_index:
                return query_sr.offset((int(page_index)-1)*5).limit(int(page_index)*5).all()
            else:
                return query_sr.all()
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}
