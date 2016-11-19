#! -*- coding: UTF-8 -*-

from skee_t.conf import CONF
from skee_t.utils.u import U

__author__ = 'rensikun'

import xml.etree.cElementTree as ET


class MyXml:
    def __init__(self):
        pass

    @staticmethod
    def gen(mydict):
        # <xml>
        # <appid>wx2421b1c4370ec43b</appid>
        # <attach>支付测试</attach>
        # <body>JSAPI支付测试</body>
        # <mch_id>10000100</mch_id>
        # <detail><![CDATA[{ "goods_detail":[ { "goods_id":"iphone6s_16G", "wxpay_goods_id":"1001", "goods_name":"iPhone6s 16G", "quantity":1, "price":528800, "goods_category":"123456", "body":"苹果手机" }, { "goods_id":"iphone6s_32G", "wxpay_goods_id":"1002", "goods_name":"iPhone6s 32G", "quantity":1, "price":608800, "goods_category":"123789", "body":"苹果手机" } ] }]]></detail>
        # <nonce_str>1add1a30ac87aa2db72f57a2375d8fec</nonce_str>
        # <notify_url>http://wxpay.weixin.qq.com/pub_v2/pay/notify.v2.php</notify_url>
        # <openid>oUpF8uMuAJO_M2pxb1Q9zNjWeS6o</openid>
        # <out_trade_no>1415659990</out_trade_no>
        # <spbill_create_ip>14.23.150.211</spbill_create_ip>
        # <total_fee>1</total_fee>
        # <trade_type>JSAPI</trade_type>
        # <sign>0CB01533B8C1EF103065174F50BCA001</sign>
        # </xml>
        mydict['appid'] = CONF.wxp.appid
        mydict['mch_id'] = CONF.wxp.mch_id
        mydict['device_info'] = CONF.wxp.device_info

        mydict['nonce_str'] = U.gen_uuid()
        mydict['sign_type'] = 'MD5'
        mydict['body'] = '滑雪帮-教学费'
        mydict['notify_url'] = CONF.wxp.notify_url
        mydict['trade_type'] = CONF.wxp.trade_type

        # 签名
        mydict['sign'] = U.sign_md5(mydict)

        xml = ET.Element('xml')
        for attr in mydict:
            ET.SubElement(xml, attr).text = mydict[attr]
        return ET.tostring(xml, 'utf-8')

    @staticmethod
    def gensimple(mydict):
        # <xml>
        # <return_code><![CDATA[SUCCESS]]></return_code>
        # <return_msg><![CDATA[OK]]></return_msg>
        # </xml>
        xml = ET.Element('xml')
        for attr in mydict:
            ET.SubElement(xml, attr).text = mydict[attr]
        return ET.tostring(xml, 'utf-8')

    @staticmethod
    def parse(otherxml):
        tree = ET.fromstring(otherxml)
        mydict = dict()
        sign = None
        for child_of_tree in tree:
            if child_of_tree.tag != 'sign':
                mydict[child_of_tree.tag] = child_of_tree.text
            else:
                sign = child_of_tree.text

        if not sign:
            return mydict
        mydict['my_sign'] = U.sign_md5(mydict)
        mydict['sign'] = sign
        return mydict
