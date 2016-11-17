#! -*- coding: UTF-8 -*-

import logging

from webob import Response

from skee_t.db.models import User
from skee_t.db.wrappers import MsgWrapper
from skee_t.services.service_msg import MsgService
from skee_t.services.services import UserService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class Msg_V1(Router):

    def __init__(self, mapper):
        super(Msg_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/{target_open_id}/{page_index}',
                       controller=Resource(controller_v1),
                       action='list_by_target_id',
                       conditions={'method': ['GET']})
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

    def list_by_target_id(self, request, target_open_id, page_index):
        LOG.info('Current received message is target_id:%s page_index:%s' % (target_open_id, page_index))
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        user = UserService().get_user(target_open_id)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        msgs = MsgService().getList(user.uuid, page_index)
        if isinstance(msgs, list):
            rsp_dict['msgs'] = [MsgWrapper(item) for item in msgs]
        else:
            rsp_dict['rspCode'] = msgs['rst_code']
            rsp_dict['rspDesc'] = msgs['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))