#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import now

from skee_t.db import DbEngine
from skee_t.db.models import Order
from skee_t.services import BaseService
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class OrderService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_order(self, desc, teach_id, pay_user_id, collect_user_id, fee):
        """
        创建订单方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        # 1 检查是否已存在订单,只要存在就直接返回
        # 0：初始；1：预支付；2：平台代收成功; 3: 平台代收失败；4：代付预支付 5：平台代付成功 6：平台代付失败 -1：预退款 -2:退款成功
        try:
            session = DbEngine.get_session_simple()
            order_exists = session.query(Order).filter(Order.teach_id ==teach_id,
                                                       Order.collect_user_id==collect_user_id,
                                                       Order.state != -2).one()
            LOG.warn("order_exists. order_no is %s" % order_exists.order_no)
            return order_exists
        except NoResultFound as e:
            # 走后续创建订单逻辑
            LOG.exception("order_exists not.")
        except Exception as e:
            LOG.exception("query Order error.")
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code':rst_code, 'rst_desc':rst_desc}

        # 2 产生新订单
        order_no = U.gen_order_no()
        order = Order(order_no=order_no,
                      desc=desc,
                      teach_id=teach_id,
                      pay_user_id=pay_user_id,
                      collect_user_id=collect_user_id,
                      fee=fee,
                      create_time=now()
                      )
        try:
            session.add(order)
            session.commit()
            return order
        except Exception as e:
            LOG.exception("Create Order error.")
            order_no = None
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc, 'order_no':order_no}

    def get_order(self, order_no=None, teach_id=None, collect_user_id=None):
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            qr = session.query(Order)
            if order_no:
                qr = qr.filter(Order.order_no == order_no)
            if teach_id:
                qr = qr.filter(Order.teach_id == teach_id)
            if collect_user_id:
                qr = qr.filter(Order.collect_user_id == collect_user_id)
            return qr.one()
        except NoResultFound as e:
            rst_code = 100000
            rst_desc = '订单不存在'
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_order(self, order_no, state, collect_id):
        session = None
        try:
            session = DbEngine.get_session_simple()
            session.query(Order) \
                .filter(Order.order_no == order_no) \
                .update({Order.state:state, Order.collect_id:collect_id}, synchronize_session=False)
            session.commit
        except NoResultFound as e:
            LOG.exception("order_not_exists error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}