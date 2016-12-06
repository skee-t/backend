#! -*- coding: UTF-8 -*-

import logging

from skee_t.task.service_pay import PayService
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizPayV1(object):

    def __init__(self):
        pass

    # order_wait_payfor_teacher
    def pre_pay(self, acts, user_ip):
        payService = PayService()
        order_no_list = list()
        do_biz = False
        for index in range(len(acts)):
            # 1.1 首个元素 且 非最后一个元素 则 追加订单号后继续循环
            # 1.2 非首个元素 且 非最后一个元素 且 当前元素的activity_id与前一个相同 则 追加后继续循环
            # 1.3 当前元素的activity_id与前一个不相同 则业务处理 置空订单号缓冲区 再 追加当前订单号后继续循环
            # 1.4 当前元素是最后一个元素 且 数组总长度<15 则业务处理
            if order_no_list.__len__() == 0 and index+1 != len(acts):
                order_no_list.append(acts[index].__getattribute__('order_no'))
                continue
            elif acts[index-1].__getattribute__('activity_id') == acts[index].__getattribute__('activity_id') \
                    and index+1 != len(acts):
                order_no_list.append(acts[index].__getattribute__('order_no'))
                continue
            elif acts[index-1].__getattribute__('activity_id') != acts[index].__getattribute__('activity_id'):
                do_biz = True
                open_id = acts[index-1].__getattribute__('open_id')
                amount = acts[index-1].__getattribute__('fee')*order_no_list.__len__()*100
                title = acts[index-1].__getattribute__('title')
            elif index+1 == len(acts) and len(acts) < 15:
                do_biz = True
                order_no_list.append(acts[index].__getattribute__('order_no'))
                open_id = acts[index].__getattribute__('open_id')
                amount = acts[index].__getattribute__('fee')*order_no_list.__len__()*100
                title = acts[index].__getattribute__('title')

            if do_biz:
                # 2 初始化代付流水,更新订单(Order.state:4代付预支付,Order.collect_id代付流水号)
                create_rst = payService.create(uuid=U.gen_uuid(), order_no_list=order_no_list,
                                               nonce_str=U.gen_uuid(),
                                               amount=amount,
                                               user_ip=user_ip,
                                               openid=open_id,
                                               desc='滑雪帮-%s-教学费用' % title)
                if create_rst:
                    LOG.error('[task]pay_for_teacher...:%s' % create_rst)
                if index+1 != len(acts):
                    order_no_list = list()
                    order_no_list.append(acts[index].__getattribute__('order_no'))

