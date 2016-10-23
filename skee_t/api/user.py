#! -*- coding: UTF-8 -*-
import json
import logging
from webob import Response
from skee_t.services.services import UserService
from skee_t.wsgi import Router
from skee_t.wsgi import Resource

__author__ = 'pluto'


LOG = logging.getLogger(__name__)


class UserApi_V1(Router):

    def __init__(self, mapper):
        super(UserApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/create_user',
                       controller=Resource(controller_v1),
                       action='create_user',
                       conditions={'method': ['POST']})
        # mapper.connect('/list',
        #                controller=wsgi.Resource(controller_v1),
        #                action='list',
        #                conditions={'method': ['GET']})
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
        resp_body = {'result': rst}

        return Response(body=json.dumps(resp_body))
