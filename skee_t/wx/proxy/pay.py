# -*- coding: utf-8 -*-
# filename: basic.py
import logging

import requests

from skee_t.conf import CONF
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_xml import MyXml

LOG = logging.getLogger(__name__)


class PayProxy(object):

    @classmethod
    def prepay(self, open_id, user_ip, attach, out_trade_no, total_fee):
        req_wx_dict = dict()
        req_wx_dict['spbill_create_ip'] = user_ip
        req_wx_dict['openid'] = open_id
        req_wx_dict['attach'] = attach
        req_wx_dict['out_trade_no'] = out_trade_no
        req_wx_dict['total_fee'] = total_fee

        req_wx_dict['trade_type'] = CONF.wxp.trade_type
        req_wx_dict['device_info'] = CONF.wxp.device_info
        req_wx_dict['body'] = '滑雪帮-教学费'
        req_wx_dict['notify_url'] = CONF.wxp.notify_url
        req_xml = MyXml.gen(req_wx_dict)

        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_unifiedorder, data = req_xml)
        LOG.info('rece %s' % r.content)

        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        # rsp_wx_dict = MyXml.parse(
        # '<xml><return_code><![CDATA[SUCCESS]]></return_code>'
        # '<return_msg><![CDATA[OK]]></return_msg>'
        # '<appid><![CDATA[wxef220312f0b51521]]></appid>'
        # '<mch_id><![CDATA[1397441502]]></mch_id>'
        # '<device_info><![CDATA[WEB]]></device_info>'
        # '<nonce_str><![CDATA[ZAaHhFCU68t3b9ZK]]></nonce_str>'
        # '<sign><![CDATA[71853E8184A02FD88EDB7992D4BA5549]]></sign>'
        # '<result_code><![CDATA[SUCCESS]]></result_code>'
        # '<prepay_id><![CDATA[wx201611181444371e4128f3b40025620664]]></prepay_id>'
        # '<trade_type><![CDATA[JSAPI]]></trade_type>'
        # '</xml>'
        # )

        if rsp_wx_dict['return_code'] != 'SUCCESS':
            LOG.warn('order_pay_exception %s %s' %(out_trade_no, rsp_wx_dict['return_msg']))
            raise MyException(700000, '系统异常,请稍微再试')

        elif rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_pay_exception ' + open_id)
            raise MyException(800000, '系统安全异常')

        elif rsp_wx_dict['result_code'] != 'SUCCESS':
            LOG.warn('order_pay_exception ' + open_id)
            raise MyException(rsp_wx_dict['err_code'], rsp_wx_dict['err_code_des'])

        return rsp_wx_dict

    @classmethod
    def query(self, transaction_id = None, out_trade_no = None):
        req_wx_dict = dict()
        if transaction_id:
            req_wx_dict['transaction_id'] = transaction_id
        if out_trade_no:
            req_wx_dict['out_trade_no'] = out_trade_no
        req_xml = MyXml.gen(req_wx_dict)
        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_orderquery, data = req_xml)
        LOG.info('rece %s' % r.content)

        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        # rsp_wx_dict = MyXml.parse(
        # '<xml><return_code><![CDATA[SUCCESS]]></return_code>'
        # '<return_msg><![CDATA[OK]]></return_msg>'
        # '<appid><![CDATA[wxef220312f0b51521]]></appid>'
        # '<mch_id><![CDATA[1397441502]]></mch_id>'
        # '<device_info><![CDATA[WEB]]></device_info>'
        # '<nonce_str><![CDATA[ZAaHhFCU68t3b9ZK]]></nonce_str>'
        # '<sign><![CDATA[71853E8184A02FD88EDB7992D4BA5549]]></sign>'
        # '<result_code><![CDATA[SUCCESS]]></result_code>'
        # '<prepay_id><![CDATA[wx201611181444371e4128f3b40025620664]]></prepay_id>'
        # '<trade_type><![CDATA[JSAPI]]></trade_type>'
        # '</xml>'
        # )

        if rsp_wx_dict['return_code'] != 'SUCCESS':
            LOG.warn('order_query_exception %s %s' %(out_trade_no, rsp_wx_dict['return_msg']))
            raise MyException(700000, '系统异常,请稍微再试')

        elif rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_query_exception ' + out_trade_no)
            raise MyException(800000, '系统安全异常')

        return rsp_wx_dict