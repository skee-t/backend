#! -*- coding: UTF-8 -*-
import json
from webob import Response
from skee_t.wsgi import Router
from skee_t.wsgi import Resource

__author__ = 'pluto'


class API_V1(Router):

    def __init__(self, mapper):
        super(API_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/create',
                       controller=Resource(controller_v1),
                       action='create',
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

    def create(self, request):
        print 'The method ----> %s' % request.method
        print 'The content type ----> %s' % request.content_type
        print 'The body ----> %s' % request.json_body
        print request.json_body['name']
        print request.json['name']
        print type(request.json)
        name = {"aaaa": "bbbb"}
        response_str = json.dumps(name)
        return Response(body=response_str)
