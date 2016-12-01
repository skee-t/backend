#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.util import KeyedTuple

from skee_t.bizs.biz_msg import BizMsgV1
from skee_t.db.models import Order
from skee_t.utils.my_exception import MyException
from skee_t.utils.u import U
from skee_t.wx.pay.service_order import OrderService
from skee_t.wx.pay.service_refund import RefundService
from skee_t.wx.proxy.refund import RefundProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizRefundV1(object):

    def __init__(self):
        pass

    def refund_pre(self, teach_id, collect_user_id):
        order = OrderService().get_order(teach_id=teach_id,collect_user_id=collect_user_id)
        if not isinstance(order, Order):
            raise MyException(order['rst_code'], order['rst_desc'])

        # 订单 -2:已退款 -1:预退款
        if order.state in [-2, -1]:
            raise MyException(100000, '预退款已成功')
        elif order.state != 2:
            raise MyException(200000, '待退款订单状态异常')

        refund_id = U.gen_refund_id()
        nonce_str = U.gen_uuid()
        create_refund_rst = RefundService().create(refund_id, order.collect_id, nonce_str, order.fee)
        if create_refund_rst:
            raise MyException(create_refund_rst['rst_code'], create_refund_rst['rst_desc'])

    def refund(self, order_refund):
        refundService = RefundService()
        # 更新当前订单处理中
        update_rst = refundService.update_process(order_refund.uuid)
        if update_rst:
            LOG.error(update_rst)
            raise MyException(update_rst['rst_code'], update_rst['rst_desc'])

        rsp_wx_dict = RefundProxy.refund(order_refund.uuid, order_refund.collect_id,
                                         order_refund.amount, order_refund.nonce_str)

        # 2 更新退款流水状态(OrderRefund.state:2退款申请成功 3:退款申请失败)
        update_rst = RefundService().update(
            collect_id=order_refund.collect_id,
            refund_id=order_refund.uuid,
            partner_refund_id = rsp_wx_dict['refund_id'] if 'refund_id' in rsp_wx_dict else None,
            refund_state = (2 if rsp_wx_dict['result_code']=='SUCCESS' else 3) if 'result_code' in rsp_wx_dict else None,
            return_code = rsp_wx_dict['return_code'] if 'return_code' in rsp_wx_dict else None,
            return_msg= rsp_wx_dict['return_msg'] if 'return_msg' in rsp_wx_dict else None,
            result_code= rsp_wx_dict['result_code'] if 'result_code' in rsp_wx_dict else None,
            err_code= rsp_wx_dict['err_code'] if 'err_code' in rsp_wx_dict else None,
            err_code_des= rsp_wx_dict['err_code_des'] if 'err_code_des' in rsp_wx_dict else None)

        if update_rst:
            raise MyException(update_rst['rst_code'], update_rst['rst_desc'])

        if rsp_wx_dict['return_code'] != 'SUCCESS':
            raise MyException(700000, '系统异常,请稍微再试')

        if rsp_wx_dict['result_code']!='SUCCESS':
            raise MyException(700000, '系统异常,请稍微再试')


    '''
    查询退款实际状态
    '''
    def query(self, order_refund):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        rsp_wx_dict = RefundProxy.query(refund_id=order_refund.uuid)

        # 更新退款流水状态(OrderRefund.state:4退款成功 5:退款失败), 如何退款成功则更新订单(Order.state:-2)
        refund_state = None
        err_code = None
        refundService = RefundService()
        if 'err_code_des' in rsp_wx_dict:
            err_code = rsp_wx_dict['err_code']
        if 'refund_status_0' in rsp_wx_dict:
            if rsp_wx_dict['refund_status_0']=='SUCCESS':
                refund_state = 4
            elif rsp_wx_dict['refund_status_0']=='FAIL':
                refund_state = 5
            else:
                err_code = rsp_wx_dict['refund_status_0']

        update_rst = refundService.update(
            collect_id=order_refund.collect_id,
            refund_id=order_refund.uuid,
            partner_refund_id = rsp_wx_dict['refund_id'] if 'refund_id' in rsp_wx_dict else None,
            refund_state = refund_state,
            return_code = rsp_wx_dict['return_code'] if 'return_code' in rsp_wx_dict else None,
            return_msg= rsp_wx_dict['return_msg'] if 'return_msg' in rsp_wx_dict else None,
            result_code= rsp_wx_dict['result_code'] if 'result_code' in rsp_wx_dict else None,
            err_code= err_code,
            err_code_des= rsp_wx_dict['err_code_des'] if 'err_code_des' in rsp_wx_dict else None)

        if update_rst:
            raise MyException(update_rst['rst_code'], update_rst['rst_desc'])

        if rsp_wx_dict['return_code'] != 'SUCCESS':
            raise MyException(700000, '系统异常,请稍微再试')

        if rsp_wx_dict['result_code']!='SUCCESS':
            raise MyException(700000, '系统异常,请稍微再试')

        # 退款成功通知
        if refund_state and refund_state == 4:
            refundMsgParams = refundService.getRefundMsgParams(order_refund.collect_id)
            if not isinstance(refundMsgParams, KeyedTuple):
                raise MyException(refundMsgParams['rst_code'], refundMsgParams['rst_desc'])

            order_dict = dict()
            order_dict['order_no'] = order_refund.uuid
            order_dict['amount'] = '%s元' % (order_refund.amount/100)
            BizMsgV1.notify_wx_temp_msg(type=8,
                                        target_id=refundMsgParams.__getattribute__('target_id'),
                                        target_name=refundMsgParams.__getattribute__('target_name'),
                                        activity_id=refundMsgParams.__getattribute__('activity_id'),
                                        activity_title=refundMsgParams.__getattribute__('activity_title'),
                                        target_open_id=refundMsgParams.__getattribute__('target_open_id'),
                                        order_dict=order_dict)

        return rsp_dict

