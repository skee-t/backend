#! -*- coding: UTF-8 -*-
import logging

from webob import Response

from skee_t.db.models import User
from skee_t.db.wrappers import UserWrapper
from skee_t.services.services import UserService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'pluto'


LOG = logging.getLogger(__name__)


class UserApi_V1(Router):

    def __init__(self, mapper):
        super(UserApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='create_user',
                       conditions={'method': ['POST']})
        mapper.connect('/authInfo/{userId}',
                       controller=Resource(controller_v1),
                       action='get_user_auth_info',
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

    def create_user(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        service = UserService()
        rst = service.create_user(req_json)
        LOG.info('The result of create user information is %s' % rst)
        rsp_dict = {'result': rst}

        return Response(body=MyJson.dumps(rsp_dict))

    def get_user_auth_info(self, request, userId):
        LOG.info('Current received message is %s' % userId)
        service = UserService()
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        rst = service.get_user_auth_info(userId)
        if isinstance(rst, User):
            rst = UserWrapper(rst)
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rst)
        rsp_dict = {'result': rst}

        return Response(body=MyJson.dumps(rsp_dict))