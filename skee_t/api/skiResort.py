#! -*- coding: UTF-8 -*-
import json
import logging

from webob import Response

from skee_t.db.wrappers import SkiResortWrapper
from skee_t.services.service_skiResort import SkiResortService
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SkiResortApi_V1(Router):

    def __init__(self, mapper):
        super(SkiResortApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='add_ski_resort',
                       conditions={'method': ['POST']})
        mapper.connect('/{page_index}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort',
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

    def add_ski_resort(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        service = SkiResortService()
        rst = service.create_skiResort(req_json)
        LOG.info('The result of create user information is %s' % rst)

        rsp_body = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=json.dumps(rsp_body))

    def list_ski_resort(self, request, page_index):
        print 'page_index:%s' % page_index
        service = SkiResortService()

        rst = service.list_skiResort(page_index)
        if isinstance(rst, list):
            rst = [SkiResortWrapper(item) for item in rst]

        LOG.info('The result of create user information is %s' % rst)

        return Response(body=json.dumps(rst, ensure_ascii=False))
