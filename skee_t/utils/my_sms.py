#! -*- coding: UTF-8 -*-
import logging

import top.api

__author__ = 'rensikun'

LOG = logging.getLogger(__name__)

class SMS:
    def __init__(self):
        pass

    @staticmethod
    def send(extend, sms_template_code, sms_param):
        req=top.api.AlibabaAliqinFcSmsNumSendRequest()
        req.set_app_info(top.appinfo("23488606","c5c966984e6296b7da091c182ac476de"))

        req.extend="123456"
        req.sms_type="normal"
        req.sms_free_sign_name="大鱼测试"
        req.sms_param="{\"code\":\"1635\",\"product\":\"滑雪帮\"}"
        req.rec_num="18600363459"
        req.sms_template_code="SMS_19005004"
        try:
            resp= req.getResponse()
            print(resp)
        except Exception,e:
            print(e)

    @staticmethod
    def send_auth_code(phone_no, auth_code):
        req=top.api.AlibabaAliqinFcSmsNumSendRequest()
        req.set_app_info(top.appinfo("23488606","c5c966984e6296b7da091c182ac476de"))

        req.rec_num=phone_no
        req.sms_param=("{\"code\":\""+auth_code+"\",\"product\":\"[滑雪帮]\"}")

        req.extend="1"
        req.sms_type="normal"
        req.sms_free_sign_name="大鱼测试"
        req.sms_template_code="SMS_19005004"

        rst_code = 0
        rst_desc = 'success'
        try:
            resp = req.getResponse()
            LOG.info("phone_no:%s rst:%s" %(phone_no, resp))
            rst_code=resp['alibaba_aliqin_fc_sms_num_send_response']['result']['err_code']
            if not resp['alibaba_aliqin_fc_sms_num_send_response']['result']['success']:
                rst_desc='failed'

            return {'rst_code': rst_code, 'rst_desc': rst_desc, 'request_id':resp['alibaba_aliqin_fc_sms_num_send_response']['request_id']}
        except Exception as e:
            LOG.exception("send_auth_code")
            # 发送异常
            rst_code = '999999'
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc}