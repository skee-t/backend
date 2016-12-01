#! -*- coding: UTF-8 -*-

import datetime
import logging

# from sqlalchemy.sql.expression import func, text
from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import Order, OrderPay, OrderRefund
from skee_t.services import BaseService
from skee_t.utils.my_exception import MyException

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class RefundService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create(self, uuid, collect_id, nonce_str, amount):
        """
        创建订单方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None

        try:
            session = DbEngine.get_session_simple()
            # 0 检查退款流水状态
            order_refund_exists = None
            try:
                order_refund_exists = session.query(OrderRefund).filter(OrderRefund.collect_id==collect_id).one()
            except NoResultFound as e:
                pass
            if order_refund_exists:
                # 0:初始 1:退款处理中 2:退款申请接收成功 3:退款申请接收失败 4:退款成功 5:退款失败
                if order_refund_exists.state == 4:
                    order_state = -2 # 退款已成功
                else:
                    order_state = -1 # 退款预处理
                session.query(Order) \
                    .filter(Order.collect_id == collect_id) \
                    .update({Order.state:order_state, Order.update_time:datetime.datetime.now()},
                            synchronize_session=False)
                session.commit()
                return {'rst_code':100000, 'rst_desc':'预退款已成功'}

            # 1 创建支付流水
            order_refund = OrderRefund(uuid=uuid,
                                       nonce_str=nonce_str,
                                       collect_id=collect_id,
                                       amount=amount
                                       )
            session.add(order_refund)
            # 2 更新订单的代付流水号,状态置为-1:预退款
            session.query(Order) \
                .filter(Order.collect_id == collect_id)\
                .update({Order.state:-1, Order.update_time:datetime.datetime.now()},
                        synchronize_session=False)
            session.commit()
        except Exception as e:
            LOG.exception("Create Order error.")
            order_no = None
            rst_code = 999999
            rst_desc = '服务异常,请联系客服'
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def update_process(self, refund_id):
        session = None
        try:
            session = DbEngine.get_session_simple()
            # 1 更新退款流水(1:退款处理中)
            update_count = session.query(OrderRefund) \
                .filter(OrderRefund.uuid == refund_id) \
                .update({OrderRefund.state:1, OrderRefund.update_time:datetime.datetime.now()},
                        synchronize_session=False)
            session.commit()
            if update_count != 1:
                raise MyException(999999,'退款流水状态异常')
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update(self, collect_id, refund_id, partner_refund_id = None, refund_state = None,
                return_code = None, return_msg= None, result_code= None,
                err_code= None, err_code_des= None):
        session = None
        try:
            session = DbEngine.get_session_simple()
            # 1 更新退款流水
            order_refund = session.query(OrderRefund) \
                .filter(OrderRefund.uuid == refund_id).one()
            if return_code:
                order_refund.return_code = return_code
            if return_msg:
                order_refund.return_msg = return_msg
            if result_code:
                order_refund.result_code = result_code
            if err_code:
                order_refund.err_code = err_code
            if err_code_des:
                order_refund.err_code_des = err_code_des
            if partner_refund_id:
                order_refund.partner_refund_id = partner_refund_id
            if refund_state:
                order_refund.state = refund_state

            # 2 实际退款成功时,更新退款订单状态-2:退款成功
            if refund_state == 4:
                session.query(Order)\
                    .filter(Order.collect_id == collect_id, Order.state == -1) \
                    .update({Order.state:-2, Order.update_time:datetime.datetime.now()},
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