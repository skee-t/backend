#! -*- coding: UTF-8 -*-
import logging
import time

from webob import Response

from skee_t.bizs.biz_msg import BizMsgV1
from skee_t.task.service_pay import PayService
from skee_t.task.service_task import TaskService
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_json import MyJson
from skee_t.utils.u import U
from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wx.pay.biz_refund import BizRefundV1
from skee_t.wx.pay.service_refund import RefundService
from skee_t.wx.proxy.pay import PayProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class TaskApiRefund_V1(Router):

    def __init__(self, mapper):
        super(TaskApiRefund_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        # 退款
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='refund',
                       conditions={'method': ['GET']})

        # 退款查询
        mapper.connect('/query',
                       controller=Resource(controller_v1),
                       action='query',
                       conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    '''
    退款
    '''
    def refund(self, request):
        LOG.info('[task]...s')
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        service = TaskService()
        # 1 待退款订单(state:0)
        order_refunds = service.list_order_refund(state=0, page_index=1, page_size=15);
        LOG.info('list_order_wait_refund is %s' % order_refunds)
        if not isinstance(order_refunds, list):
            rsp_dict['rspCode'] = order_refunds['rst_code']
            rsp_dict['rspDesc'] = order_refunds['rst_desc']
            LOG.info('[task]...e:%s' % rsp_dict)
            return Response(body=MyJson.dumps(rsp_dict))

        bizRefund = BizRefundV1()
        for order_refund in order_refunds:
            try:
                bizRefund.refund(order_refund)
            except MyException as mye:
                LOG.exception("refund error %s %s "% (mye.code, mye.desc))
            except Exception as e:
                LOG.exception("refund error.")

        LOG.info('[task]...e')
        return Response(body=MyJson.dumps(rsp_dict))


    '''
    对退款受理成功但还未有结果的退款订单发起查询
    '''
    def query(self, request):
        LOG.info('[task]...s')
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        service = TaskService()
        # 1 待查看订单(微信退款申请受理成功state:2)
        order_refunds = service.list_order_refund(state=2, page_index=1, page_size=15);
        LOG.info('list_order_wait_refund is %s' % order_refunds)
        if not isinstance(order_refunds, list):
            rsp_dict['rspCode'] = order_refunds['rst_code']
            rsp_dict['rspDesc'] = order_refunds['rst_desc']
            LOG.info('[task]...e:%s' % rsp_dict)
            return Response(body=MyJson.dumps(rsp_dict))

        bizRefund = BizRefundV1()
        for order_refund in order_refunds:
            try:
                bizRefund.query(order_refund)
            except MyException:
                LOG.exception("refund error %s %s "% (MyException.code, MyException.desc))
            except Exception:
                LOG.exception("refund error.")
        LOG.info('[task]...e')
        return Response(body=MyJson.dumps(rsp_dict))