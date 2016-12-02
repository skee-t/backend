#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import User, Order, OrderCollect, ActivityMember
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class CollectService(BaseService):
    """

    """

    def __init__(self):
        pass

    def create_order(self, uuid, order_no, nonce_str, attach, user_ip, openid):
        """
        创建订单方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'
        order_collect = OrderCollect(uuid=uuid,
                                     order_no=order_no,
                                     nonce_str=nonce_str,
                                     attach=attach,
                                     user_ip=user_ip,
                                     openid=openid,
                                 )
        try:
            session = DbEngine.get_session_simple()
            # 1 创建支付流水
            session.add(order_collect)
            # 2 更新订单支付流水号
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.collect_id = uuid
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
            order_collect = session.query(OrderCollect) \
                .filter(OrderCollect.uuid == pay_id).one()
            if return_code:
                order_collect.return_code = return_code
            if return_msg:
                order_collect.return_msg = return_msg
            if result_code:
                order_collect.result_code = result_code
            if err_code:
                order_collect.err_code = err_code
            if err_code_des:
                order_collect.err_code_des = err_code_des
            if prepay_id:
                order_collect.prepay_id = prepay_id
            if state:
                order_collect.state = state
            session.commit()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update_pay_with_order(self, order_no, order_state, collect_id, state = None,
                              return_code = None, return_msg= None, result_code= None,
                   err_code= None, err_code_des= None, prepay_id= None):
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            # 更新订单支付流水
            order_collect = session.query(OrderCollect) \
                .filter(OrderCollect.uuid == collect_id).one()
            if return_code:
                order_collect.return_code = return_code
            if return_msg:
                order_collect.return_msg = return_msg
            if result_code:
                order_collect.result_code = result_code
            if err_code:
                order_collect.err_code = err_code
            if err_code_des:
                order_collect.err_code_des = err_code_des
            if prepay_id:
                order_collect.prepay_id = prepay_id
            if state:
                order_collect.state = state
            # 更新订单
            order = session.query(Order) \
                .filter(Order.order_no == order_no).one()
            order.state = order_state
            order.collect_id = collect_id

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
            return session.query(OrderCollect) \
                .filter(OrderCollect.prepay_id == prepay_id).one()
        except (TypeError, Exception) as e:
            LOG.exception("get_order error.")
            # 数据库异常
            rst_code = 999999
            rst_desc = e.message
            return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def getpay_by_collectid(self, collect_id):
        try:
            session = DbEngine.get_session_simple()
            return session.query(OrderCollect) \
                .filter(OrderCollect.uuid == collect_id).one()
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
            return session.query(OrderCollect.state, Order.state.label('order_state'), Order.order_no
                                 , Order.teach_id, Order.collect_user_id) \
                .filter(OrderCollect.uuid == pay_id) \
                .filter(OrderCollect.openid == open_id) \
                .filter(User.open_id == OrderCollect.openid) \
                .filter(Order.order_no == OrderCollect.order_no) \
                .filter(Order.collect_id == OrderCollect.uuid) \
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
            return session.query(OrderCollect.uuid, OrderCollect.openid, OrderCollect.user_ip, OrderCollect.attach, Order.fee) \
                .filter(OrderCollect.order_no == order_no) \
                .filter(OrderCollect.uuid == Order.collect_id) \
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
            order_pay = session.query(OrderCollect) \
                .filter(OrderCollect.prepay_id == prepay_id).one()
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
            order_collect = session.query(OrderCollect) \
                .filter(OrderCollect.uuid == pay_id).one()
            order_collect.return_code = 'SUCCESS'
            order_collect.state = 3
            order_collect.partner_collect_id = transaction_id

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
            order_collect = session.query(OrderCollect) \
                .filter(OrderCollect.uuid == pay_id).one()
            order_collect.return_code = 'FAIL'
            order_collect.err_code = err_code
            order_collect.err_code_des = err_code_des
            order_collect.state = 4
            if transaction_id:
                order_collect.partner_collect_id = transaction_id

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