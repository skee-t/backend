#! -*- coding: UTF-8 -*-

import logging
import uuid

from skee_t.db import DbEngine
from skee_t.db.models import SkiResort
from skee_t.services import BaseService
from skee_t.services.service_validator import SkiResortCreateValidator

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
        skiResort = SkiResort(uuid=str(uuid.uuid4()),
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
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
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
            engine = DbEngine.get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
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
