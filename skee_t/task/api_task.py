#! -*- coding: UTF-8 -*-
import logging

from webob import Response

from skee_t.bizs.biz_msg import BizMsgV1
from skee_t.task.service_task import TaskService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

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