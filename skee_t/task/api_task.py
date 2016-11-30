#! -*- coding: UTF-8 -*-
import logging

from webob import Response

from skee_t.bizs.biz_msg import BizMsgV1
from skee_t.task.service_pay import PayService
from skee_t.task.service_task import TaskService
from skee_t.utils.my_json import MyJson
from skee_t.utils.u import U
from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wx.proxy.pay import PayProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class TaskApi_V1(Router):

    def __init__(self, mapper):
        super(TaskApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        # 活动开始(没5分钟执行一次)
        mapper.connect('/activity/s',
                       controller=Resource(controller_v1),
                       action='activity_start',
                       conditions={'method': ['GET']})
        # 活动结束(每5分钟执行一次)
        mapper.connect('/activity/e',
                       controller=Resource(controller_v1),
                       action='activity_end',
                       conditions={'method': ['GET']})

        # 待晋级(每4小时执行一次)
        mapper.connect('/activity/mp',
                       controller=Resource(controller_v1),
                       action='member_wait_pro',
                       conditions={'method': ['GET']})

        # 待评价(每5小时执行一次)
        mapper.connect('/activity/mc',
                       controller=Resource(controller_v1),
                       action='teacher_wait_comment',
                       conditions={'method': ['GET']})

        # 代付预支付
        mapper.connect('/pay/teacher/pre',
                       controller=Resource(controller_v1),
                       action='pay_for_teacher_pre',
                       conditions={'method': ['GET']})

        # 代付预支付
        mapper.connect('/pay/teacher',
                       controller=Resource(controller_v1),
                       action='pay_for_teacher',
                       conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    def activity_start(self, request):
        LOG.info('[task]activity_start...s')
        service = TaskService()
        # 从满额或召集中 修改为 进行中
        ats = service.change_activity([0, 1], 2);
        LOG.info('The result of create user information is %s' % ats)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        LOG.info('[task]activity_start...e')
        return Response(body=MyJson.dumps(rsp_dict))

    def activity_end(self, request):
        LOG.info('[task]activity_end...s')
        service = TaskService()
        # 从进行中 修改为 已结束
        ats = service.change_activity_finish();
        LOG.info('The result of create user information is %s' % ats)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        LOG.info('[task]activity_end...e')
        return Response(body=MyJson.dumps(rsp_dict))

    def member_wait_pro(self, request):
        LOG.info('[task]member_wait_pro...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        service = TaskService()
        # 活动状态(3：已结束)
        # 结束时间(4小时内)
        # 队伍中有人付款(2:付款待教学)
        # 未通知过(不存在消息里)
        acts = service.list_act_wait_pro(type=1, page_index=1);
        LOG.info('list_act_wait_pro is %s' % acts)
        if isinstance(acts, list):
            for act in acts:
                try:
                    BizMsgV1().create_with_send_sms(type=5,source_id='admin_msg',source_name='小帮',
                                                    target_id=act.__getattribute__('leader_id'),
                                                    target_name=act.__getattribute__('leader_name'),
                                                    target_phone=act.__getattribute__('phone_no'),
                                                    activity_id=act.__getattribute__('activity_id'))

                except Exception as e:
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = e.message
        else:
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']

        LOG.info('[task]member_wait_pro...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def teacher_wait_comment(self, request):
        LOG.info('[task]teacher_wait_comment...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        service = TaskService()
        # 活动状态(3：已结束 4: 学员已晋级)
        # 结束时间(8小时内)
        # 成员状态(2: 已付款 3:晋级)
        acts = service.list_member_wait_comment(type=1, page_index=1);
        LOG.info('list_act_wait_pro is %s' % acts)
        if isinstance(acts, list):
            for act in acts:
                try:
                    BizMsgV1().create_with_send_sms(type=3,source_id='admin_msg',source_name='小帮',
                                                    target_id=act.__getattribute__('member_id'),
                                                    target_name=act.__getattribute__('member_name'),
                                                    target_phone=act.__getattribute__('phone_no'),
                                                    activity_id=act.__getattribute__('activity_id'))

                except Exception as e:
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = e.message
        else:
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    '''
    教学结束后,将未投诉的学员学费直接付给教学者
    '''
    def pay_for_teacher_pre(self, request):
        LOG.info('[task]pay_for_teacher...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # 用户投诉(estimate_score = -1) 订单退款(Order.state:-1)
        # 3 微信企业代付
        # 4 更新代付流水(OrderPay.state代付结果),更新订单(Order.state:5代付成功6代付失败)
        # 5 通知教练: 代付成功时通知教练
        service = TaskService()
        # 1 获取活动结束(Activity.state:3)超过24小时又短于36小时,学费代收有成功的(Order.state:2)
        acts = service.list_order_wait_payfor_teacher(type=1, page_index=1, page_size=15);
        LOG.info('list_order_wait_payfor_teacher is %s' % acts)
        user_ip = request._headers.get('Proxy-Client-IP','192.168.0.100')
        payService = PayService()
        if isinstance(acts, list):
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
                    amount = acts[index-1].__getattribute__('fee')*order_no_list.__len__()
                    title = acts[index-1].__getattribute__('title')
                elif index+1 == len(acts) and len(acts) < 15:
                    do_biz = True
                    order_no_list.append(acts[index].__getattribute__('order_no'))
                    open_id = acts[index].__getattribute__('open_id')
                    amount = acts[index].__getattribute__('fee')*order_no_list.__len__()
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
        else:
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    '''
    教学结束后,将未投诉的学员学费直接付给教学者
    '''
    def pay_for_teacher(self, request):
        LOG.info('[task]pay_for_teacher...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # 用户投诉(estimate_score = -1) 订单退款(Order.state:-1)
        # 3 微信企业代付
        # 4 更新代付流水(OrderPay.state代付结果),更新订单(Order.state:5代付成功6代付失败)
        # 5 通知教练: 代付成功时通知教练
        service = TaskService()
        # 1 获取待代付订单(OrderPay.state:0)
        order_pays = service.list_pay_wait_for_teacher(type=1, page_index=1, page_size=15);
        LOG.info('list_pay_wait_for_teacher is %s' % order_pays)
        if not isinstance(order_pays, list):
            rsp_dict['rspCode'] = order_pays['rst_code']
            rsp_dict['rspDesc'] = order_pays['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        payService = PayService()
        for order_pay in order_pays:
            rsp_wx_dict = None
            try:
                rsp_wx_dict = PayProxy.pay(order_pay.openid, order_pay.user_ip,
                                           order_pay.uuid, order_pay.desc, str(order_pay.amount))
            except Exception as e:
                LOG.exception("Create Order error.")

            # 2 初始化代付流水,更新订单(Order.state:4代付预支付,Order.collect_id代付流水号)
            update_rst = payService.update(
                pay_id=order_pay.uuid,
                partner_pay_id = rsp_wx_dict['payment_no'] if 'payment_no' in rsp_wx_dict else None,
                pay_time = rsp_wx_dict['pay_time'] if 'pay_time' in rsp_wx_dict else None,
                pay_state = (1 if rsp_wx_dict['result_code']=='SUCCESS' else 2) if 'result_code' in rsp_wx_dict else None,
                return_code = rsp_wx_dict['return_code'] if 'return_code' in rsp_wx_dict else None,
                return_msg= rsp_wx_dict['return_msg'] if 'return_msg' in rsp_wx_dict else None,
                result_code= rsp_wx_dict['result_code'] if 'result_code' in rsp_wx_dict else None,
                err_code= rsp_wx_dict['err_code'] if 'err_code' in rsp_wx_dict else None,
                err_code_des= rsp_wx_dict['err_code_des'] if 'err_code_des' in rsp_wx_dict else None)

            if update_rst:
                LOG.error('[task]pay_for_teacher...:%s' % update_rst)

        LOG.info('[task]pay_for_teacher...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))