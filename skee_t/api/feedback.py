#! -*- coding: UTF-8 -*-

import logging

from webob import Response

from skee_t.db.models import User
from skee_t.services.service_feedback import FeedbackService
from skee_t.services.services import UserService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class Feedback_V1(Router):

    def __init__(self, mapper):
        super(Feedback_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='add_feed_back',
                       conditions={'method': ['POST']})
        # mapper.connect('/detail/{id}',
        #                controller=wsgi.Resource(controller_v1),
        #                action='detail',
        #                conditions={'method': ['GET']})
        # mapper.connect('/delete/{id}',
        #                controller=wsgi.Resource(controller_v1),
        #                action='delete',
        #                conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    def add_feed_back(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # todo 获取当前用户
        user = UserService().get_user(open_id=req_json.get('openId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        req_json['userId'] = user.uuid

        rst = FeedbackService().create_feedback(req_json)
        # BizMsgV1().create_with_send_sms(type=4,source_id=source_id,source_name=source_name,
        #                                 target_id=activity_leader.__getattribute__('leader_id'),
        #                                 target_name=activity_leader.__getattribute__('leader_name'),
        #                                 target_phone=activity_leader.__getattribute__('leader_phone'),
        #                                 activity_id=req_json.get('teachId'))
        LOG.info('The result of create user information is %s' % rst)
        rsp_dict = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=MyJson.dumps(rsp_dict))