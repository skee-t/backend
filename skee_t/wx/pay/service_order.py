#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import Order, OrderPay
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
        # 订单状态 0：初始；1：预支付；2：成功; 3: 失败；
        try:
            session = DbEngine.get_session_simple()
            order_exists = session.query(Order).filter(Order.teach_id ==teach_id, Order.pay_user_id==pay_user_id).one()
            if order_exists.state == 2:
                rst_code = 200000
                rst_desc = '已支付成功'
            else:
                order_pay_exists = session.query(OrderPay).filter(OrderPay.uuid==order_exists.pay_id).one()
                if order_pay_exists.state == 2:
                    rst_code = 200001
                    rst_desc = '支付流水处理中'
            LOG.exception("order_exists. order_no is %s" % order_exists.order_no)
            return {'rst_code':rst_code, 'rst_desc':rst_desc, 'order_no':order_exists.order_no}
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
                      fee=fee
                      )
        try:
            session.add(order)
            session.commit()
        except Exception as e:
            LOG.exception("Create Order error.")
            order_no = None
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
        return {'rst_code':rst_code, 'rst_desc':rst_desc, 'order_no':order_no}

    def get_order(self, order_no):
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            return session.query(Order).filter(Order.order_no == order_no).one()
        except NoResultFound as e:
            LOG.exception("order_not_exists error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_order(self, order_no, state, pay_id):
        session = None
        try:
            session = DbEngine.get_session_simple()
            session.query(Order) \
                .filter(Order.order_no == order_no) \
                .update({Order.state:state, Order.pay_id:pay_id}, synchronize_session=False)
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