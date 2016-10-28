#! -*- coding: UTF-8 -*-

import datetime
import logging
import uuid

from webob import Response

from skee_t.conf import CONF
from skee_t.db.models import SpToken, SpCount
from skee_t.services.service_sp import SpService
from skee_t.utils.my_json import MyJson
from skee_t.utils.my_sms import SMS
from skee_t.utils.u import U
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class SP_V1(Router):

    def __init__(self, mapper):
        super(SP_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='create_sp',
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

    def create_sp(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        sp_service = SpService()

        # 判断获取验证码次数是否超限
        sp_count = sp_service.select_sp_count(req_json.get('phoneNo'))

        # 不存在,新增加sp_count
        sp_count_flag = 0
        if not sp_count:
            pass
        elif isinstance(sp_count, SpCount):
            if sp_count.last_time + datetime.timedelta(hours=1)>datetime.datetime.now():
                if sp_count.times >= CONF.sp.auth_code_limit:
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = '验证码获取次数超限,请1小时后再试'
                    return Response(body=MyJson.dumps(rsp_dict))
                elif sp_count.last_time + datetime.timedelta(seconds=30) > datetime.datetime.now():
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = '验证码获取太频繁,请慢慢来'
                    return Response(body=MyJson.dumps(rsp_dict))
                else:
                    # 有效时间内,需times+1
                    sp_count_flag = 1
            else:
                # 已超过1小时,属过期,需重置times=1
                sp_count_flag = 2
        else:
            rsp_dict['rspCode'] = sp_count['rst_code']
            rsp_dict['rspDesc'] = sp_count['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        token = str(uuid.uuid4())
        auth_code = U.gen_auth_code_num()
        # 发送短信
        sms_rst = SMS.send_auth_code(req_json.get('phoneNo'), auth_code)
        # 记录结果
        sp_token = SpToken(
            token=token,
            phone_no=req_json.get('phoneNo'),
            auth_code=auth_code,
            template_code=sms_rst['template_code'],
            state=0 if (int(sms_rst['rst_code'])) == 0 else -1,
            request_id=sms_rst['request_id']
        )
        sp_service.create_sp(sp_token, sp_count_flag)

        if sms_rst:
            rsp_dict['rspCode'] = sms_rst['rst_code']
            rsp_dict['rspDesc'] = sms_rst['rst_desc']
            rsp_dict['token'] = token

        return Response(body=MyJson.dumps(rsp_dict))