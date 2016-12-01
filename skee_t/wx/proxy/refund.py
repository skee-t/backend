# -*- coding: utf-8 -*-
# filename: basic.py
import logging

import requests

from skee_t.conf import CONF
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_xml import MyXml
from skee_t.utils.u import U

LOG = logging.getLogger(__name__)


class RefundProxy(object):

    @classmethod
    def refund(self, refund_id, collect_id, total_fee, nonce_str):
        req_wx_dict = dict()
        req_wx_dict['appid'] = CONF.wxp.appid
        req_wx_dict['mch_id'] = CONF.wxp.mch_id
        req_wx_dict['nonce_str'] = nonce_str
        req_wx_dict['sign_type'] = 'MD5'

        req_wx_dict['out_trade_no'] = collect_id
        req_wx_dict['out_refund_no'] = refund_id
        req_wx_dict['total_fee'] = str(total_fee)  # 单位分
        req_wx_dict['refund_fee'] = str(total_fee)   # 单位分
        req_wx_dict['op_user_id'] = CONF.wxp.mch_id
        # 签名
        req_wx_dict['sign'] = U.sign_md5(req_wx_dict)

        req_xml = MyXml.gensimple(req_wx_dict)
        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_refund,
                           data = req_xml, verify=True,
                           cert=(CONF.wxp.pay_crt, CONF.wxp.pay_key))
        LOG.info('rece %s' % r.content)
        '''
        <xml><return_code><![CDATA[SUCCESS]]></return_code>
        <return_msg><![CDATA[OK]]></return_msg>
        <appid><![CDATA[wxef220312f0b51521]]></appid>
        <mch_id><![CDATA[1397441502]]></mch_id>
        <nonce_str><![CDATA[uVqWKiTuAiewaa7y]]></nonce_str>
        <sign><![CDATA[493D264D05288AEC22850F9FBBB7C13D]]></sign>
        <result_code><![CDATA[SUCCESS]]></result_code>
        <transaction_id><![CDATA[4007552001201611291161528242]]></transaction_id>
        <out_trade_no><![CDATA[29bda9e2509e4242ab6106f1388c615b]]></out_trade_no>
        <out_refund_no><![CDATA[b33b3bbd0fb5412c841b05b0cf2d463c]]></out_refund_no>
        <refund_id><![CDATA[2007552001201612010618818612]]></refund_id>
        <refund_channel><![CDATA[]]></refund_channel>
        <refund_fee>100</refund_fee>
        <coupon_refund_fee>0</coupon_refund_fee>
        <total_fee>100</total_fee>
        <cash_fee>100</cash_fee>
        <coupon_refund_count>0</coupon_refund_count>
        <cash_refund_fee>100</cash_refund_fee>
        </xml>
        '''

        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        if 'my_sign' in rsp_wx_dict and rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_refund_exception ' + refund_id)
            raise MyException(800000, '系统安全异常')
        return rsp_wx_dict

    @classmethod
    def query(self, refund_id):
        req_wx_dict = dict()
        req_wx_dict['appid'] = CONF.wxp.appid
        req_wx_dict['mch_id'] = CONF.wxp.mch_id
        req_wx_dict['nonce_str'] = U.gen_uuid()
        req_wx_dict['out_refund_no'] = refund_id

        # 签名
        req_wx_dict['sign'] = U.sign_md5(req_wx_dict)
        req_xml = MyXml.gensimple(req_wx_dict)
        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_refundquery,
                           data = req_xml, verify=True,
                           cert=(CONF.wxp.pay_crt, CONF.wxp.pay_key))
        LOG.info('rece %s' % r.content)
        # <xml>
        # <return_code><![CDATA[SUCCESS]]></return_code>
        # <result_code><![CDATA[SUCCESS]]></result_code>
        # <partner_trade_no><![CDATA[c07d089291bd4178b24c7d83212936cf]]></partner_trade_no>
        # <mch_id>1397441502</mch_id>
        # <detail_id><![CDATA[1000018301201611275147619807]]></detail_id>
        # <status><![CDATA[SUCCESS]]></status>
        # <openid><![CDATA[o2pJcvz6msVs08t49EU8zsLjAaXo]]></openid>
        # <payment_amount>100</payment_amount>
        # <transfer_time><![CDATA[2016-11-27 17:55:18]]></transfer_time>
        # <desc><![CDATA[滑雪帮-教学费用代付给教练]]></desc>
        # <return_msg><![CDATA[获取成功]]></return_msg>
        # </xml>
        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        if 'my_sign' in rsp_wx_dict and rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_refund_query_exception ' + refund_id)
            raise MyException(800000, '系统安全异常')

        return rsp_wx_dict

# reload(sys)
# sys.setdefaultencoding('utf-8')
# PayProxy.pay('o2pJcvz6msVs08t49EU8zsLjAaXo','60.205.167.51','c07d089291bd4178b24c7d83212936ch', '【松花湖·单板】小鹿乱撞的小鹿队','100')
# PayProxy.query('c07d089291bd4178b24c7d83212936cf')