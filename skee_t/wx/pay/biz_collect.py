#! -*- coding: UTF-8 -*-

import logging

from skee_t.db.models import User
from skee_t.services.services import UserService
from skee_t.wx.pay.service_collect import CollectService
from skee_t.wx.pay.service_order import OrderService
from skee_t.wx.proxy.collect import CollectProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizPayV1(object):

    def __init__(self):
        pass

    def pre_pay(self, user_ip, open_id, attach, check_order):
        pass

    '''
    1 支付流水状态为[同步OK] 当商户后台、网络、服务器等出现异常，商户系统最终未接收到支付通知；
    2 支付流水状态为[同步不OK] 用户需要重新支持,且在调用关单或撤销接口API之前，需确认支付状态
    3 支付流水状态为[同步异常] 调用支付接口后，返回系统错误或未知交易状态情况；
    '''
    def query(self, transaction_id, pay_id, order_no, activity_uuid, user_uuid):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        queryRst = CollectProxy.query(transaction_id=transaction_id, out_trade_no=pay_id)
        if queryRst['result_code'] != 'SUCCESS':
            if queryRst['err_code'] == 'ORDERNOTEXIST':
                pass
            else:
                rsp_dict['rspCode'] = 999999
                rsp_dict['rspDesc'] = '系统异常，请稍后再试'
                return rsp_dict
        else:
            # SUCCESS—支付成功
            # REFUND—转入退款
            # NOTPAY—未支付
            # CLOSED—已关闭
            # REVOKED—已撤销（刷卡支付）
            # USERPAYING--用户支付中
            # PAYERROR--支付失败(其他原因，如银行返回失败)
            urst = None
            pay_service = CollectService()
            if queryRst['trade_state'] == 'SUCCESS':
                # 3.1更新流水及订单成功
                #    更改成员状态为已付款
                LOG.warn('update_pay_by_async_success rst %s ' %(urst))
                urst = pay_service.update_pay_by_async_success( pay_id=pay_id,
                                                                order_no=order_no,
                                                                transaction_id=queryRst['transaction_id'],
                                                                activity_uuid=activity_uuid,
                                                                user_uuid=user_uuid)
                if not urst:
                    LOG.info('order already success')
                    rsp_dict['rspCode'] = 200000
                    rsp_dict['rspDesc'] = '已支付成功'
                    return rsp_dict
            else:
                # 3.2 更新流水及订单失败
                urst = pay_service.update_pay_by_async_fail(pay_id=pay_id,
                                                            order_no=order_no,
                                                            transaction_id= (queryRst['transaction_id'] if queryRst.has_key('transaction_id') else None),
                                                            err_code=queryRst['trade_state'],
                                                            err_code_des=queryRst['trade_state_desc'])
                if urst:
                    LOG.warn('update_pay_by_async_fail rst %s ' %(urst))
        return rsp_dict

    '''
    1 商户订单支付失败需要生成新单号重新发起支付，要对原订单号调用关单，避免重复支付
    2 系统下单后，用户支付超时，系统退出不再受理，避免用户继续，请调用关单接口。
    注意：订单生成后不能马上调用关单接口，最短调用时间间隔为5分钟。
    '''
    def close(self, open_id, order_no):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        user = UserService().get_user(open_id)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return rsp_dict

        order_service = OrderService()
        order = order_service.get_order(order_no=order_no)

        if order.collect_id != user.uuid:
            LOG.warn('order_user_wrong ' + open_id)
            rsp_dict['rspCode'] = 999999
            rsp_dict['rspDesc'] = '信息检验错误,请确保是本人支付'
            return rsp_dict

        if order.state == 2:
            LOG.warn('order_pay_success_yet ' + open_id)
            rsp_dict['rspCode'] = 200000
            rsp_dict['rspDesc'] = '已支付成功'
            return rsp_dict
        return order

