#! -*- coding: UTF-8 -*-
import logging

from webob import Response

from skee_t.db.wrappers import SkiResortWrapper, SkiResortSimpleWrapper
from skee_t.services.service_skiResort import SkiResortService
from skee_t.utils.my_json import MyJson
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
        mapper.connect('/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort',
                       conditions={'method': ['GET']})
        mapper.connect('/near/{openid}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort_near',
                       conditions={'method': ['GET']})
        mapper.connect('/often/{userId}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort_often',
                       conditions={'method': ['GET']})
        mapper.connect('/simple/{skiType}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_ski_resort_simple',
                       conditions={'method': ['GET']})
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

        rsp_dict = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=MyJson.dumps(rsp_dict))

    def list_ski_resort(self, request, city=None, pageIndex=None):
        print 'page_index:%s' % pageIndex
        service = SkiResortService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.list_skiResort(city=city, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [SkiResortWrapper(item) for item in rst]
            rsp_dict['skiResorts'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def list_ski_resort_near(self, request, openid, pageIndex):
        # todo 通过openid从微信结果获取位置
        return self.list_ski_resort(request, '河北市', pageIndex)


    def list_ski_resort_often(self, request, userId, pageIndex):
        # todo userId
        service = SkiResortService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.list_skiResort_often(user_id=userId, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [SkiResortWrapper(item) for item in rst]
            rsp_dict['skiResorts'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    def list_ski_resort_simple(self, request, skiType, pageIndex=None):
        print 'page_index:%s' % pageIndex
        service = SkiResortService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.list_skiResort_simple(ski_type=skiType, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [SkiResortSimpleWrapper(item) for item in rst]
            rsp_dict['skiResortSimples'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))