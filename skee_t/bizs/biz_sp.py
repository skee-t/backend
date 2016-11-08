#! -*- coding: UTF-8 -*-

import datetime
import logging

from skee_t.conf import CONF
from skee_t.db.models import SpToken, SpCount
from skee_t.services.service_sp import SpService
from skee_t.utils.my_sms import SMS
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizSpV1(object):

    def __init__(self):
        pass

    def send(self, phone_no):
        LOG.info('BizSpV1 param is %s' % phone_no)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        sp_service = SpService()

        # 判断获取验证码次数是否超限
        sp_count = sp_service.select_sp_count(phone_no)

        # 不存在,新增加sp_count
        sp_count_flag = 0
        if not sp_count:
            pass
        elif isinstance(sp_count, SpCount):
            if sp_count.last_time + datetime.timedelta(hours=1)>datetime.datetime.now():
                if sp_count.times >= CONF.sp.auth_code_limit:
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = '验证码获取次数超限,请1小时后再试'
                    return rsp_dict
                elif sp_count.last_time + datetime.timedelta(seconds=30) > datetime.datetime.now():
                    rsp_dict['rspCode'] = 999999
                    rsp_dict['rspDesc'] = '验证码获取太频繁,请慢慢来'
                    return rsp_dict
                else:
                    # 有效时间内,需times+1
                    sp_count_flag = 1
            else:
                # 已超过1小时,属过期,需重置times=1
                sp_count_flag = 2
        else:
            rsp_dict['rspCode'] = sp_count['rst_code']
            rsp_dict['rspDesc'] = sp_count['rst_desc']
            return rsp_dict

        token = U.gen_uuid()
        auth_code = U.gen_auth_code_num()
        # 发送短信
        sms_rst = SMS.send_auth_code(phone_no, auth_code)
        # 记录结果
        sp_token = SpToken(
            token=token,
            phone_no=phone_no,
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

        return rsp_dict