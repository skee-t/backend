#! -*- coding: UTF-8 -*-

import datetime
import logging

# from sqlalchemy.sql.expression import func, text

from skee_t.db import DbEngine
from skee_t.db.models import Order, OrderPay
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class PayService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create(self, uuid, order_no_list, nonce_str, amount, user_ip, openid, desc):
        """
        创建订单方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'
        order_pay = OrderPay(uuid=uuid,
                             nonce_str=nonce_str,
                             user_ip=user_ip,
                             openid=openid,
                             check_name='NO_CHECK',
                             amount=amount,
                             desc=desc
                                     )
        try:
            session = DbEngine.get_session_simple()
            # 1 创建支付流水
            session.add(order_pay)
            # 2 更新订单的代付流水号,状态置为4-代付预支付
            session.query(Order) \
                .filter(Order.order_no.in_(order_no_list))\
                .update({Order.pay_id:uuid, Order.state:4, Order.update_time:datetime.datetime.now()},
                        synchronize_session=False)
            session.commit()
        except Exception as e:
            LOG.exception("Create Order error.")
            order_no = None
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc, 'order_no':order_no}

    def update(self, pay_id, partner_pay_id = None, pay_time = None, pay_state = None,
                return_code = None, return_msg= None, result_code= None,
                err_code= None, err_code_des= None):
        session = None
        try:
            session = DbEngine.get_session_simple()
            # 1 更新代付流水
            order_pay = session.query(OrderPay) \
                .filter(OrderPay.uuid == pay_id).one()
            if return_code:
                order_pay.return_code = return_code
            if return_msg:
                order_pay.return_msg = return_msg
            if result_code:
                order_pay.result_code = result_code
            if err_code:
                order_pay.err_code = err_code
            if err_code_des:
                order_pay.err_code_des = err_code_des
            if partner_pay_id:
                order_pay.partner_pay_id = partner_pay_id
            if pay_time:
                order_pay.pay_time = pay_time
            if pay_state:
                order_pay.state = pay_state

            # 2 更新订单状态5-代付成功,6-代付失败
            session.query(Order)\
                .filter(Order.pay_id == pay_id, Order.state == 4) \
                .update({Order.state:(5 if pay_state==1 else 6), Order.update_time:datetime.datetime.now()},
                        synchronize_session=False)

            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code': rst_code, 'rst_desc': rst_desc}