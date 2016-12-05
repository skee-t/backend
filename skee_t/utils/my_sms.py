#! -*- coding: UTF-8 -*-
import logging

import top.api
from skee_t.conf import CONF

__author__ = 'rensikun'

LOG = logging.getLogger(__name__)


class SMS:

    def __init__(self):
        pass

    @staticmethod
    def send_auth_code(phone_no, auth_code):
        # 模板类型: 验证码
        # 模板名称: 身份验证验证码
        # 模板ID: SMS_19005008
        # 模板内容: 验证码${code}，您正在进行${product}身份验证，打死不要告诉别人哦！
        return SMS.send(phone_no, "SMS_19005008", "{\"code\":\""+auth_code+"\",\"product\":\"<滑雪帮>\"}")

    @staticmethod
    def send_notify_apply(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 新成员入队提醒
        # 模板ID: SMS_26120182
        # 模板内容: 亲爱的${dstname}：${srcname}申请入队，请您抽空审核。详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        # 申请说明: 队员加入小队待审核
        return SMS.send(phone_no, "SMS_26120182", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send_notify_approve(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 队长批准提醒
        # 模板ID: SMS_26150367
        # 模板内容: 亲爱的${dstname}：您已被${srcname}批准入队，还差一步就能得到大神的指点。详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        # 申请说明: 队长批准队员，队员待付款
        return SMS.send(phone_no, "SMS_26150367", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send_notify_stu_commit(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 成员评价提醒
        # 模板ID: SMS_26225297
        # 模板内容: 亲爱的${dstname}：得到${srcname}指点后是否身轻如燕~赶快来评价一下TA~详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        return SMS.send(phone_no, "SMS_26225297", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send_notify_tea_commit(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 成员评价通知
        # 模板ID: SMS_26110147
        # 模板内容: 亲爱的${dstname}：有人评价了您，赶快来看看~详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        # 申请说明: 活动结束后成员对队长评价
        return SMS.send(phone_no, "SMS_26110147", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send_notify_tea_pro(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 成员评级提醒
        # 模板ID: SMS_26280261
        # 模板内容: 亲爱的${dstname}：请给您的本期学员评级~详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        # 申请说明: 成员等级晋升
        return SMS.send(phone_no, "SMS_26280261", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send_notify_stu_pro(phone_no, dstname, srcname):
        # 模板类型: 短信通知
        # 模板名称: 成员晋级通知
        # 模板ID: SMS_26155288
        # 模板内容: 亲爱的${dstname}：恭喜你完成晋级~详情：滑雪帮公众号-我-我的消息。滑雪帮，让滑雪更美好~
        # 申请说明: 成员晋级
        return SMS.send(phone_no, "SMS_26155288", "{\"dstname\":\""+dstname+"\",\"srcname\":\""+srcname+"\"}")

    @staticmethod
    def send(phone_no, sms_template_code, sms_param):
        rst_code = 0
        rst_desc = 'success'
        request_id = ''

        LOG.info("CONF.sp.switch:%s" % CONF.sp.switch)
        # if not CONF.sp.switch:
        #     return {'rst_code': rst_code, 'rst_desc': rst_desc, 'template_code' : '', 'request_id' : request_id}
        req=top.api.AlibabaAliqinFcSmsNumSendRequest()
        req.set_app_info(top.appinfo("23488606","c5c966984e6296b7da091c182ac476de"))

        req.rec_num=phone_no
        req.sms_param=sms_param

        req.extend="1"
        req.sms_type="normal"
        req.sms_free_sign_name="万里阳光"
        req.sms_template_code= sms_template_code

        try:
            resp = req.getResponse()
            LOG.info("phone_no:%s rst:%s" %(phone_no, resp))
            rst_code=resp['alibaba_aliqin_fc_sms_num_send_response']['result']['err_code']
            if not resp['alibaba_aliqin_fc_sms_num_send_response']['result']['success']:
                rst_desc='failed'
            request_id = resp['alibaba_aliqin_fc_sms_num_send_response']['request_id']
        except Exception as e:
            LOG.exception("send_auth_code")
            # 发送异常
            rst_code = 999999
            rst_desc = e.message
        return {'rst_code': rst_code, 'rst_desc': rst_desc, 'template_code':req.sms_template_code,
                'request_id':request_id}

if __name__ == '__main__':
    # SMS.send_auth_code('18600363459', '123456')
    SMS.send_auth_code('+31652726236', '237834')