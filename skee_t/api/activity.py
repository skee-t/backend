#! -*- coding: UTF-8 -*-
import json
import logging

from webob import Response

from skee_t.db.wrappers import ActivityWrapper
from skee_t.services.service_activity import ActivityService
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class ActivityApi_V1(Router):

    def __init__(self, mapper):
        super(ActivityApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/teach',
                       controller=Resource(controller_v1),
                       action='add_activity_teach',
                       conditions={'method': ['POST']})
        mapper.connect('/{skiResortUUID}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort_activity',
                       conditions={'method': ['GET']})
        mapper.connect('/near/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort_near',
                       conditions={'method': ['GET']})
        mapper.connect('/often/{pageIndex}',
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

    def add_activity_teach(self, request):
        #todo 获取当前用户
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        service = ActivityService()
        req_json['type'] = 1
        req_json['creator'] = 'xm'

        rst = service.create_activity_teach(req_json)
        LOG.info('The result of create user information is %s' % rst)

        rsp_body = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=json.dumps(rsp_body))

    def list_ski_resort_activity(self, request, skiResortUUID=None, pageIndex=None):
        print 'page_index:%s' % pageIndex
        service = ActivityService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.list_skiResort_activity(skiResort_uuid=skiResortUUID, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['skiResorts'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=json.dumps(rsp_dict, ensure_ascii=False))

    def list_ski_resort_near(self, request, page_index):
        #todo 获取当前用户所在城市
        return self.list_ski_resort(request, '河北市', page_index)


