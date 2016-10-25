#! -*- coding: UTF-8 -*-
import json
import logging

from webob import Response

from skee_t.services.service_skiResort import SkiResortService
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SkiResortApi_V1(Router):

    def __init__(self, mapper):
        super(SkiResortApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/add',
                       controller=Resource(controller_v1),
                       action='add_skiResort',
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

    def add_skiResort(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        service = SkiResortService()
        rst = service.create_skiResort(req_json)
        LOG.info('The result of create user information is %s' % rst)

        rspBody = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=json.dumps(rspBody))
