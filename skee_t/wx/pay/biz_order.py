#! -*- coding: UTF-8 -*-

import logging

from skee_t.db.models import User
from skee_t.services.services import UserService
from skee_t.wx.pay.service_order import OrderService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizOrderV1(object):

    def __init__(self):
        pass

    def check(self, open_id, order_no):
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

