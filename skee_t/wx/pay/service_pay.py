#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import User, Order, OrderPay, ActivityMember
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class PayService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_pay_order(self, uuid, order_no, nonce_str, attach, user_ip, openid):
        """
        创建订单方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'
        order_pay = OrderPay(uuid=uuid,
                             order_no=order_no,
                             nonce_str=nonce_str,
                             attach=attach,
                             user_ip=user_ip,
                             openid=openid,
                      )
        try:
            session = DbEngine.get_session_simple()
            # 1 创建支付流水
            session.add(order_pay)
            # 2 更新订单支付流水号
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.pay_id = uuid
            session.commit()
        except Exception as e:
            LOG.exception("Create Order error.")
            order_no = None
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code':rst_code, 'rst_desc':rst_desc, 'order_no':order_no}

    def update_pay(self, pay_id, state = None, return_code = None, return_msg= None, result_code= None,
                   err_code= None, err_code_des= None, prepay_id= None):
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
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
            if prepay_id:
                order_pay.prepay_id = prepay_id
            if state:
                order_pay.state = state
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_pay_with_order(self, order_no, order_state, pay_id, state = None,
                              return_code = None, return_msg= None, result_code= None,
                   err_code= None, err_code_des= None, prepay_id= None):
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            # 更新订单支付流水
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
            if prepay_id:
                order_pay.prepay_id = prepay_id
            if state:
                order_pay.state = state
            # 更新订单
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.state = order_state
            order.pay_id = pay_id

            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def getpay_by_prepayid(self, prepay_id = None):
        try:
            session = DbEngine.get_session_simple()
            # 更新订单支付
            return session.query(OrderPay) \
                .filter(OrderPay.prepay_id == prepay_id).one()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def getpay_by_payid(self, pay_id = None):
        try:
            session = DbEngine.get_session_simple()
            return session.query(OrderPay) \
                .filter(OrderPay.uuid == pay_id).one()
        except NoResultFound as e:
            LOG.exception("getpay_by_payid non-one.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def getpay_by_userpayid(self, open_id = None, pay_id = None):
        try:
            session = DbEngine.get_session_simple()
            return session.query(OrderPay.state,Order.state.label('order_state'), Order.order_no
                                 ,Order.teach_id, Order.pay_user_id) \
                .filter(OrderPay.uuid == pay_id) \
                .filter(OrderPay.openid == open_id) \
                .filter(User.open_id == OrderPay.openid) \
                .filter(Order.order_no == OrderPay.order_no) \
                .filter(Order.pay_id == OrderPay.uuid) \
                .one()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def getpay_by_order(self, order_no):
        try:
            session = DbEngine.get_session_simple()
            return session.query(OrderPay.uuid, OrderPay.openid, OrderPay.user_ip, OrderPay.attach, Order.fee) \
                .filter(OrderPay.order_no == order_no) \
                .filter(OrderPay.uuid == Order.pay_id) \
                .one()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_pay_by_sync(self, prepay_id = None, return_code = None, return_msg= None):
        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            order_pay = session.query(OrderPay) \
                .filter(OrderPay.prepay_id == prepay_id).one()
            if return_code:
                order_pay.return_code = return_code
            if return_msg:
                order_pay.return_msg = return_msg
            if return_msg == 'get_brand_wcpay_request：ok':
                order_pay.state = 2
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_pay_by_async_success(self, pay_id, order_no, transaction_id, activity_uuid, user_uuid):
        session = None
        try:
            session = DbEngine.get_session_simple()
            # 1 更新流水状态
            order_pay = session.query(OrderPay) \
                .filter(OrderPay.uuid == pay_id).one()
            order_pay.return_code = 'SUCCESS'
            order_pay.state = 3
            order_pay.partner_pay_id = transaction_id

            # 2 更新订单状态
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.state = 2

            # 3 更新成员状态 2-已经付款
            activity_member = session.query(ActivityMember) \
                .filter(ActivityMember.activity_uuid == activity_uuid,
                        ActivityMember.user_uuid == user_uuid).one()
            activity_member.state = 2

            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("update_pay_by_async_success error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_pay_by_async_fail(self, pay_id, order_no, transaction_id, err_code, err_code_des):
        session = None
        try:
            session = DbEngine.get_session_simple()
            # 1 更新流水状态
            order_pay = session.query(OrderPay) \
                .filter(OrderPay.uuid == pay_id).one()
            order_pay.return_code = 'FAIL'
            order_pay.err_code = err_code
            order_pay.err_code_des = err_code_des
            order_pay.state = 4
            if transaction_id:
                order_pay.partner_pay_id = transaction_id

            # 2 更新订单状态
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.state = 3

            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("update_pay_by_async_success error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            if session is not None:
                session.rollback()
            return {'rst_code': rst_code, 'rst_desc': rst_desc}