#! -*- coding: UTF-8 -*-
import logging

from sqlalchemy.util import KeyedTuple
from webob import Response

from skee_t.db.wrappers import ActivityWrapper
from skee_t.services.service_activity import ActivityService
from skee_t.services.service_skiResort import SkiResortService
from skee_t.utils.my_json import MyJson
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
        mapper.connect('/teach/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_activity_teach',
                       conditions={'method': ['GET']})
        mapper.connect('/myTeach/{userId}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_activity_myteach',
                       conditions={'method': ['GET']})
        mapper.connect('/all/{skiResortId}/{pageIndex}',
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
        req_json['creator'] = '428fcb9b-e958-4109-98f7-bc9b76789079'

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        ski_resort = SkiResortService().list_skiResort(uuid=req_json.get('skiResortId'))
        if not isinstance(ski_resort, KeyedTuple):
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '雪场不存在'
        else:
            rst = service.create_activity_teach(req_json)
            LOG.info('The result of create user information is %s' % rst)
            rsp_dict['rspCode'] = rst.get('rst_code')
            rsp_dict['rspDesc'] = rst.get('rst_desc')

        return Response(body=MyJson.dumps(rsp_dict))

    def list_ski_resort_activity(self, request, skiResortId=None, pageIndex=None):
        print 'page_index:%s' % pageIndex
        service = ActivityService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        ski_resort = SkiResortService().list_skiResort(uuid=skiResortId)
        if not isinstance(ski_resort, KeyedTuple):
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '雪场不存在'
        else:
            rst = service.list_skiResort_activity(skiResort_uuid = skiResortId,page_index=pageIndex)
            if isinstance(rst, list):
                rst = [ActivityWrapper(item) for item in rst]
                rsp_dict['activitys'] = rst
                rsp_dict['skiResortName'] = ski_resort.__getattribute__('name')
                rsp_dict['trailPic'] = ski_resort.__getattribute__('trail_pic')
            else:
                rsp_dict['rspCode'] = rst['rst_code']
                rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def list_activity_teach(self, request, leaderId=None, pageIndex=None):
        #todo 获取当前用户所在城市
        print 'list_activity_teach page_index:%s' % pageIndex
        service = ActivityService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.list_skiResort_activity(type=1, leader_id=leaderId, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['teachings'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    def list_activity_myteach(self, request, userId, pageIndex):
        #todo 获取当前用户所在城市
        print 'list_activity_myteach page_index:%s' % pageIndex
        return self.list_activity_teach(request,leaderId=userId,pageIndex=pageIndex)
