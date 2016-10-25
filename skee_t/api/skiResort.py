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
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='add_ski_resort',
                       conditions={'method': ['POST']})
        mapper.connect('/list',
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

        rspBody = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=json.dumps(rspBody))

    def list_ski_resort(self, request):
        LOG.info('Current received message is %s' % request.GET)
        service = SkiResortService()
        rst = service.list_skiResort(request.GET['pageIndex'])
        LOG.info('The result of create user information is %s' % rst)
        print json.dumps(class_to_dict(rst), skipkeys=True)

        # print MyJEncoder().encode(rst)
        return Response(body=json.dumps(class_to_dict(rst)))

def convert_to_dict(obj):
    '''把Object对象转换成Dict对象'''
    dict = {}
    dict.update(obj.__dict__)
    return dict


def convert_to_dicts(objs):
    '''把对象列表转换为字典列表'''
    obj_arr = []

    for o in objs:
        #把Object对象转换成Dict对象
        dict = {}
        dict.update(o.__dict__)
        obj_arr.append(dict)

    return obj_arr


def class_to_dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            #把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict
