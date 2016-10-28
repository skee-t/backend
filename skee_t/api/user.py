#! -*- coding: UTF-8 -*-
import datetime
import logging

from webob import Response

from skee_t.db.models import User
from skee_t.db.wrappers import UserWrapper
from skee_t.services.service_sp import SpService
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
        mapper.connect('/authInfo',
                       controller=Resource(controller_v1),
                       action='add_user_auth_info',
                       conditions={'method': ['POST']})
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

    # todo remove when on-line
    def create_user(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        service = UserService()
        rst = service.create_user(req_json, 'test-', '')
        LOG.info('The result of create user information is %s' % rst)
        rsp_dict = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=MyJson.dumps(rsp_dict))

    def get_user_auth_info(self, request, userId):
        LOG.info('Current received message is %s' % userId)
        service = UserService()
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        rst = service.get_user_auth_info(userId)
        if isinstance(rst, User):
            rst = UserWrapper(rst)
            rsp_dict.update(rst)
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def add_user_auth_info(self, request):
        LOG.info('Current received message is %s' % request.json_body)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # 校验手机验证码
        spService = SpService()
        sp_token = spService.select_sp_token(request.json_body['phoneNo'], request.json_body['token'])
        if not sp_token:
            rsp_dict['rspCode'] = 100002
            rsp_dict['rspDesc'] = '上传的参数不正确'
            return Response(body=MyJson.dumps(rsp_dict))

        elif sp_token.__getattribute__('last_time') + datetime.timedelta(minutes=10) < datetime.datetime.now()\
                or sp_token.__getattribute__('state') == 1:
            rsp_dict['rspCode'] = 100003
            rsp_dict['rspDesc'] = '验证码已经过期'
            return Response(body=MyJson.dumps(rsp_dict))

        state = 0  # 待验证
        if sp_token.__getattribute__('verify_count') >= 3:
            rsp_dict['rspCode'] = 100004
            rsp_dict['rspDesc'] = '验证码超过最大验证次数,请重新发送验证码'
            state = 2  # 验证失败
        elif sp_token.__getattribute__('auth_code') != request.json_body['authCode']:
            rsp_dict['rspCode'] = 100003
            rsp_dict['rspDesc'] = '验证码不正确'
            state = 0  # 待验证
        else:
            state = 1  # 验证通过

        spService.update_sp(request.json_body['phoneNo'], request.json_body['token'], state)
        if rsp_dict['rspCode'] != 0:
            return Response(body=MyJson.dumps(rsp_dict))

        # 增加用户
        # todo 从微信接口获取当前用户的用户名及OPENID
        service = UserService()
        user_dict = dict()
        user_dict['name'] = 'test-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        user_dict['open_id'] = 'openid'
        user_dict.update(request.json_body)

        rst = service.create_user(user_dict)
        LOG.info('The result of create user information is %s' % rst)
        rsp_dict = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
        return Response(body=MyJson.dumps(rsp_dict))