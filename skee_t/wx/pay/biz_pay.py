#! -*- coding: UTF-8 -*-

import logging

import requests

from skee_t.conf import CONF
from skee_t.db.models import User
from skee_t.services.services import UserService
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_xml import MyXml
from skee_t.wx.pay.service_order import OrderService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizPayV1(object):

    def __init__(self):
        pass

    def pre_pay(self, user_ip, open_id, attach, check_order):

        req_wx_dict = dict()
        req_wx_dict['spbill_create_ip'] = user_ip
        req_wx_dict['openid'] = open_id
        req_wx_dict['attach'] = attach
        req_wx_dict['out_trade_no'] = check_order.order_no
        req_wx_dict['total_fee'] = check_order.fee
        req_xml = MyXml.gen(req_wx_dict)

        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_unifiedorder, data = req_xml)
        LOG.info('rece %s' % r.content)

        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        if rsp_wx_dict['return_code'] != 'SUCCESS':
            LOG.warn('order_pay_exception %s %s' %(check_order.order_no, rsp_wx_dict['return_msg']))
            raise MyException(700000, '系统异常,请稍微再试')
        elif rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_pay_exception ' + open_id)
            raise MyException(800000, '系统安全异常')
        elif rsp_wx_dict['result_code'] != 'SUCCESS':
            LOG.warn('order_pay_exception ' + open_id)
            raise MyException(rsp_wx_dict['err_code'], rsp_wx_dict['err_code_des'])

        return req_wx_dict

    '''
    1 支付流水状态为[同步OK] 当商户后台、网络、服务器等出现异常，商户系统最终未接收到支付通知；
    2 支付流水状态为[同步不OK] 用户需要重新支持,且在调用关单或撤销接口API之前，需确认支付状态
    3 支付流水状态为[同步异常] 调用支付接口后，返回系统错误或未知交易状态情况；
    '''
    def query(self, open_id, order_no):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        user = UserService().get_user(open_id)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return rsp_dict

        order_service = OrderService()
        order = order_service.get_order(order_no)

        if order.pay_id != user.uuid:
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
        order = order_service.get_order(order_no)

        if order.pay_id != user.uuid:
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

