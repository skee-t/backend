#! -*- coding: UTF-8 -*-
import logging
import time

from webob import Response

from skee_t.bizs.biz_msg import BizMsgV1
from skee_t.task.service_pay import PayService
from skee_t.task.service_task import TaskService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wx.pay.biz_pay import BizPayV1
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

        # 代付预支付(学员都评价了)
        mapper.connect('/pay/teacher/pre_e',
                       controller=Resource(controller_v1),
                       action='pay_for_teacher_pre_early',
                       conditions={'method': ['GET']})

        # 代付预支付(学员有未评价,活动结束12~18小时)
        mapper.connect('/pay/teacher/pre_l',
                       controller=Resource(controller_v1),
                       action='pay_for_teacher_pre_late',
                       conditions={'method': ['GET']})

        # 代付预支付
        mapper.connect('/pay/teacher',
                       controller=Resource(controller_v1),
                       action='pay_for_teacher',
                       conditions={'method': ['GET']})

        # 为教练统计付款学员及金额
        mapper.connect('/pay/stat',
                       controller=Resource(controller_v1),
                       action='statistics_fee_for_teacher',
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
                    BizMsgV1().notify_wx_temp_msg(type=5,
                                                  target_open_id=act.__getattribute__('leader_open_id'),
                                                  target_id=act.__getattribute__('leader_id'),
                                                  target_name=act.__getattribute__('leader_name'),
                                                  activity_id=act.__getattribute__('activity_id'),
                                                  activity_title=act.__getattribute__('activity_title'))
                    # BizMsgV1().create_with_send_sms(type=5,source_id='admin_msg',source_name='小帮',
                    #                                 target_id=act.__getattribute__('leader_id'),
                    #                                 target_name=act.__getattribute__('leader_name'),
                    #                                 target_phone=act.__getattribute__('phone_no'),
                    #                                 activity_id=act.__getattribute__('activity_id'))

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
        LOG.info('teacher_wait_comment is %s' % acts)
        if isinstance(acts, list):
            for act in acts:
                try:
                    BizMsgV1().notify_wx_temp_msg(type=3,
                                                  target_open_id=act.__getattribute__('member_open_id'),
                                                  target_id=act.__getattribute__('member_id'),
                                                  target_name=act.__getattribute__('member_name'),
                                                  activity_id=act.__getattribute__('activity_id'),
                                                  activity_title=act.__getattribute__('activity_title'))
                    # BizMsgV1().create_with_send_sms(type=3,source_id='admin_msg',source_name='小帮',
                    #                                 target_id=act.__getattribute__('member_id'),
                    #                                 target_name=act.__getattribute__('member_name'),
                    #                                 target_phone=act.__getattribute__('phone_no'),
                    #                                 activity_id=act.__getattribute__('activity_id'))

                except Exception as e:
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = e.message
        else:
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    # todo
    def statistics_fee_for_teacher(self, request):
        LOG.info('[task]...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        service = TaskService()
        # 活动状态(0：召集中)
        # 时间(活动开始前1小时)
        acts = service.list_activity_pay(type=1, page_index=1);
        LOG.info('teacher_wait_comment is %s' % acts)
        if not isinstance(acts, list):
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']

        for act in acts:
            try:
                # 成员状态(2: 已付款)
                member_names = service.list_member_pay(act.__getattribute__('activity_id'))
                if not isinstance(member_names, list):
                    LOG.warn('member_names error %s' % member_names)
                    continue

                members = ''
                for member_name in member_names:
                    if members != '':
                        members+=','
                    members+=member_name.__getattribute__('member_name')

                order_dict = dict()
                order_dict['amount'] = '%0.0f元' % (act.__getattribute__('amount') * member_names.__len__())

                # target_name,activity_title,members,amount,target_open_id,activity_id
                BizMsgV1().notify_wx_temp_msg(type=9, target_name=act.__getattribute__('leader_name'),
                                              activity_title=act.__getattribute__('activity_title'),
                                              order_dict=order_dict,
                                              source_name=members,
                                              target_open_id=act.__getattribute__('leader_open_id'),
                                              target_id=act.__getattribute__('leader_id'),
                                              activity_id=act.__getattribute__('activity_id'),
                                              )

            except Exception as e:
                rsp_dict['rspCode'] = 999999
                rsp_dict['rspDesc'] = e.message

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    '''
    教学结束后,将未投诉的学员学费直接付给教学者
    1 活动结束(Activity.state:3)
    2 学费代收成功的(Order.state:2)
    3 用户未投诉(ActivityMember.state(2,3) estimate_score != -1)
    4 不存在已缴费但未评价的学员(ActivityMember.estimate_score != 0)
    -> 初始化代付订单
    '''
    def pay_for_teacher_pre_early(self, request):
        LOG.info('[task]...s')
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # 订单退款(Order.state:-1)
        service = TaskService()
        acts = service.list_order_wait_payfor_teacher_early(type=1, page_index=1, page_size=15);
        LOG.info('list_order_wait_payfor_teacher_early is %s' % acts)
        user_ip = request._headers.get('Proxy-Client-IP','192.168.0.100')
        if not isinstance(acts, list):
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']
        elif acts.__len__() > 0:
            BizPayV1().pre_pay(acts, user_ip)

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    '''
    教学结束后,将未投诉的学员学费直接付给教学者
    1 活动结束(Activity.state:3)
    2 结束时间超过12小时又短于18小时(Activity.update_time(12h,18h))
    3 学费代收成功的(Order.state:2)
    4 用户未投诉(ActivityMember.estimate_score != -1)
    -> 初始化代付订单
    '''
    def pay_for_teacher_pre_late(self, request):
        LOG.info('[task]pay_for_teacher...s')

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # 订单退款(Order.state:-1)
        service = TaskService()
        acts = service.list_order_wait_payfor_teacher_late(type=1, page_index=1, page_size=15);
        LOG.info('list_order_wait_payfor_teacher_late is %s' % acts)
        user_ip = request._headers.get('Proxy-Client-IP','192.168.0.100')
        if not isinstance(acts, list):
            rsp_dict['rspCode'] = acts['rst_code']
            rsp_dict['rspDesc'] = acts['rst_desc']
        else:
            BizPayV1().pre_pay(acts, user_ip)

        LOG.info('[task]teacher_wait_comment...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    '''
    教学结束后,将未投诉的学员学费直接付给教学者
    3 微信企业代付
    4 更新代付流水(OrderPay.state代付结果),更新订单(Order.state:5代付成功6代付失败)
    5 通知教练: 代付成功时通知教练
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
        user_pre = None
        for order_pay in order_pays:
            rsp_wx_dict = None
            if user_pre and user_pre == order_pay.openid:
                LOG.info('same pay for user-wait for 16 seconds')
                time.sleep(16)
            else:
                LOG.info('different pay for user-wait for 1 seconds')
                user_pre = order_pay.openid
                time.sleep(1)

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
            else:
                # 通知教练
                payMsgParam = payService.getPayMsgParams(order_pay.uuid)

                # 成员状态(2: 已付款)
                member_names = service.list_member_pay(payMsgParam.__getattribute__('activity_id'))
                if not isinstance(member_names, list):
                    LOG.warn('member_names error %s' % member_names)
                    continue
                members = ''
                for member_name in member_names:
                    if members != '':
                        members+=','
                    members+=member_name.__getattribute__('member_name')

                order_dict = dict()
                order_dict['amount'] = '%0.0f元' % (order_pay.amount/100)
                BizMsgV1().notify_wx_temp_msg(type=10,source_name=members,
                                          target_open_id=payMsgParam.__getattribute__('target_open_id'),
                                          target_id=payMsgParam.__getattribute__('target_id'),
                                          target_name=payMsgParam.__getattribute__('target_name'),
                                          activity_id=payMsgParam.__getattribute__('activity_id'),
                                          activity_title=payMsgParam.__getattribute__('activity_title'),
                                          order_dict=order_dict)

        LOG.info('[task]pay_for_teacher...e:%s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))
