# -*- coding: utf-8 -*-
# filename: basic.py
import logging

import requests

from skee_t.conf import CONF
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_xml import MyXml
from skee_t.utils.u import U

LOG = logging.getLogger(__name__)


class PayProxy(object):

    @classmethod
    def pay(self, open_id, user_ip, pay_id, desc, amount):
        req_wx_dict = dict()
        req_wx_dict['mch_appid'] = CONF.wxp.appid
        req_wx_dict['mchid'] = CONF.wxp.mch_id
        req_wx_dict['nonce_str'] = U.gen_uuid()
        req_wx_dict['partner_trade_no'] = pay_id
        req_wx_dict['openid'] = open_id
        req_wx_dict['check_name'] = 'NO_CHECK'
        req_wx_dict['amount'] = amount   # 单位分
        req_wx_dict['desc'] = desc
        req_wx_dict['spbill_create_ip'] = user_ip
        # 签名
        req_wx_dict['sign'] = U.sign_md5(req_wx_dict)

        req_xml = MyXml.gensimple(req_wx_dict)
        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_pay,
                           data = req_xml, verify=True,
                           cert=(CONF.wxp.pay_crt, CONF.wxp.pay_key))
        LOG.info('rece %s' % r.content)

        # '<xml>'
        # '<return_code><![CDATA[SUCCESS]]></return_code>'
        # '<return_msg><![CDATA[付款金额不能小于最低限额.]]></return_msg>'
        # '<result_code><![CDATA[FAIL]]></result_code>'
        # '<err_code><![CDATA[AMOUNT_LIMIT]]></err_code>'
        # '<err_code_des><![CDATA[付款金额不能小于最低限额.]]></err_code_des>'
        # '</xml>'

        # '<xml>'
        # '<return_code><![CDATA[SUCCESS]]></return_code>'
        # '<return_msg><![CDATA[]]></return_msg>'
        # '<mch_appid><![CDATA[wxef220312f0b51521]]></mch_appid>'
        # '<mchid><![CDATA[1397441502]]></mchid>'
        # '<device_info><![CDATA[]]></device_info>'
        # '<nonce_str><![CDATA[82d610c5fd8440b99cf7c5df437752f7]]></nonce_str>'
        # '<result_code><![CDATA[SUCCESS]]></result_code>'
        # '<partner_trade_no><![CDATA[c07d089291bd4178b24c7d83212936ch]]></partner_trade_no>'
        # '<payment_no><![CDATA[1000018301201611275147910835]]></payment_no>'
        # '<payment_time><![CDATA[2016-11-27 18:20:36]]></payment_time>'
        # '</xml>'

        # 先判断协议字段返回，再判断业务返回，最后判断交易状态
        rsp_wx_dict = MyXml.parse(r.content)
        if 'my_sign' in rsp_wx_dict and rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_pay_exception ' + open_id)
            raise MyException(800000, '系统安全异常')
        return rsp_wx_dict

    @classmethod
    def query(self, pay_id):
        req_wx_dict = dict()
        req_wx_dict['nonce_str'] = U.gen_uuid()
        req_wx_dict['partner_trade_no'] = pay_id
        req_wx_dict['appid'] = CONF.wxp.appid
        req_wx_dict['mch_id'] = CONF.wxp.mch_id
        # 签名
        req_wx_dict['sign'] = U.sign_md5(req_wx_dict)
        req_xml = MyXml.gensimple(req_wx_dict)
        LOG.info('send %s' % req_xml)
        r = requests.post (CONF.wxp.i_payqeruy,
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
        if rsp_wx_dict['return_code'] != 'SUCCESS':
            LOG.warn('order_query_exception %s %s' %(pay_id, rsp_wx_dict['return_msg']))
            raise MyException(700000, '系统异常,请稍微再试')

        elif 'my_sign' in rsp_wx_dict and rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_query_exception ' + pay_id)
            raise MyException(800000, '系统安全异常')

        return rsp_wx_dict

# reload(sys)
# sys.setdefaultencoding('utf-8')
# PayProxy.pay('o2pJcvz6msVs08t49EU8zsLjAaXo','60.205.167.51','c07d089291bd4178b24c7d83212936ch', '【松花湖·单板】小鹿乱撞的小鹿队','100')
# PayProxy.query('c07d089291bd4178b24c7d83212936cf')