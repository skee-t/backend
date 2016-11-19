#! -*- coding: UTF-8 -*-
import logging
import time

from sqlalchemy.util import KeyedTuple
from webob import Response

from skee_t.conf import CONF
from skee_t.db.models import User, OrderPay
from skee_t.db.wrappers import ActivityMemberSimpleWrapper
from skee_t.services.service_activity import ActivityService
from skee_t.services.services import UserService
from skee_t.utils.my_exception import MyException
from skee_t.utils.my_json import MyJson
from skee_t.utils.my_xml import MyXml
from skee_t.utils.u import U
from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wx.pay.service_order import OrderService
from skee_t.wx.pay.service_pay import PayService
from skee_t.wx.proxy.pay import PayProxy

__author__ = 'rensikun'

LOG = logging.getLogger(__name__)


class PayApi_V1(Router):

    def __init__(self, mapper):
        super(PayApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()

        # 订单状态 0：初始；1：支付处理中；2：成功; 3: 失败;
        # 订单支付流水状态 0:初始 1:预支付 2:同步成功 3:同步失败 4:同步未知 5:异步成功 6:异步失败 7:关闭 8:未知

        # 生成订单,状态0
        # 调用微信统一下单API
        # 订单状态1
        mapper.connect('/order',
                       controller=Resource(controller_v1),
                       action='create_order',
                       conditions={'method': ['POST']})

        # 前端同步通知 订单状态 0：初始；1：支付处理中；2：成功; 3: 失败；
        mapper.connect('/notifys',
                       controller=Resource(controller_v1),
                       action='notify_sync',
                       conditions={'method': ['POST']})

        # 微信支付后端异步通知
        mapper.connect('/notifya',
                       controller=Resource(controller_v1),
                       action='notify_async',
                       conditions={'method': ['POST']})

        # 支付流水状态为[同步OK] 当商户后台、网络、服务器等出现异常，商户系统最终未接收到支付通知；
        # 支付流水状态为[同步异常] 调用支付接口后，返回系统错误或未知交易状态情况；
        # 支付流水状态为[同步不OK] 用户需要重新支持,且在调用关单或撤销接口API之前，需确认支付状态
        mapper.connect('/query',
                       controller=Resource(controller_v1),
                       action='query',
                       conditions={'method': ['POST']})

        # 青山测试
        mapper.connect('/qs',
                       controller=Resource(controller_v1),
                       action='get_user_auth_info',
                       conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    def create_order(self, request):
        LOG.info('Current received message is %s' % request.json_body)
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        open_id = request.json_body['openId']
        teach_Id = request.json_body['teachId']

        # 0 获取当前用户信息
        user_info = UserService().get_user(open_id=open_id)
        if not isinstance(user_info, User):
            rsp_dict['rspCode'] = user_info['rst_code']
            rsp_dict['rspDesc'] = user_info['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        # 1 获取小队详情
        activity_member_rst = ActivityService().activity_member(type=1,
                                                     teach_id=teach_Id,
                                                     member_id_join=user_info.uuid
                                                  )
        if not isinstance(activity_member_rst, KeyedTuple):
            return Response(body=MyJson.dumps(activity_member_rst))

        ams = ActivityMemberSimpleWrapper(activity_member_rst)

        # 2 创建订单 订单状态0
        desc = ams['title']+'教学费'
        total_fee = ams['fee']+'00'
        rst = OrderService().create_order(desc, teach_Id, pay_user_id=user_info.uuid,
                                          collect_user_id=ams['leaderId'],
                                          fee=total_fee)
        LOG.info('The result of create user information is %s' % rst)
        if rst['rst_code'] == 0:
            rsp_dict['orderNo'] = rst['order_no']
        else:
            # todo 1-预支付 是否需要限制
            # 支付已成功 支付流水处理中 其他错误
            rsp_dict = {'rspCode':rst.get('rst_code'),'rspDesc':rst.get('rst_desc')}
            return Response(body=MyJson.dumps(rsp_dict))

        # 3 微信统一下单
        # 3.1 写订单支付信息 订单支付流水状态0
        pay_service = PayService()
        attach = 'www.huaxuebang.pro'
        user_ip = request._headers.get('Proxy-Client-IP','192.168.0.100')
        pay_id = U.gen_uuid()
        # 支付流水状态 0
        cpay_rst = pay_service.create_pay(pay_id, rst['order_no'], U.gen_uuid(), attach, user_ip, open_id)
        if cpay_rst:
            rsp_dict['rspCode'] = cpay_rst.get('rst_code')
            rsp_dict['rspDesc'] = cpay_rst.get('rst_desc')
            return Response(body=MyJson.dumps(rsp_dict))

        # 2 向微信下单 成功后获取到prepay_id[预支付交易会话标识]
        try:
            rsp_wx_dict = PayProxy.prepay(open_id=open_id, user_ip=user_ip, attach=attach, order_no=pay_id, total_fee=total_fee)
        except MyException as e:
            rsp_dict['rspCode'] = e.code
            rsp_dict['rspDesc'] = e.desc

        # 3 更新订单支付信息 1[预支付]  修改平台订单状态为1[预支付]
        upay_rst = pay_service.update_pay_with_order(
                                rst['order_no'], 1, # order
                                pay_id, 1, # order pay
                               rsp_wx_dict['return_code'],rsp_wx_dict['return_msg'],
                               rsp_wx_dict['result_code'],
                               rsp_dict['rspCode'],rsp_dict['rspDesc'],
                               rsp_wx_dict['prepay_id'])
        if rsp_dict['rspCode'] != 0:
            return Response(body=MyJson.dumps(rsp_dict))
        if upay_rst['rst_code'] != 0:
            rsp_dict['rspCode'] = upay_rst.get('rst_code')
            rsp_dict['rspDesc'] = upay_rst.get('rst_desc')
            return Response(body=MyJson.dumps(rsp_dict))

        back_dict = dict()
        if rsp_wx_dict['prepay_id']:
            # 5 将以下参数返回给前端
            # "appId" ： "wx2421b1c4370ec43b",     //公众号名称，由商户传入
            # "timeStamp"：" 1395712654",         //时间戳，自1970年以来的秒数
            # "nonceStr" ： "e61463f8efa94090b1f366cccfbbb444", //随机串
            # "package" ： "prepay_id=u802345jgfjsdfgsdg888",
            # "signType" ： "MD5",         //微信签名方式：
            # "paySign" ： "70EA570631E4BB79628FBCA90534C63FF7FADD89" //微信签名
            back_dict['appId'] = CONF.wxp.appid
            back_dict['timeStamp'] = str(int(time.time()))
            back_dict['nonceStr'] = U.gen_uuid()
            back_dict['package'] = 'prepay_id='+rsp_wx_dict['prepay_id']
            back_dict['signType'] = 'MD5'
            back_dict['paySign'] = U.sign_md5(back_dict)
            back_dict['rspCode'] = 0
            back_dict['rspDesc'] = 'success'
        else:
            back_dict['rspCode'] = 800000
            back_dict['rspDesc'] = '系统异常,请稍后再试'

        LOG.info('The result information is %s' % back_dict)
        return Response(body=MyJson.dumps(back_dict))

    def notify_sync(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        prepay_id = req_json['package'].split('=')[1]
        # get_brand_wcpay_request：ok	支付成功
        # get_brand_wcpay_request：cancel	支付过程中用户取消
        # get_brand_wcpay_request：fail	支付失败
        wcpay_rst = req_json['wcpayRst']

        rsp_dict = dict([('return_code', 'SUCCESS'), ('return_msg', 'OK')])
        pay_service = PayService()
        # 1 确认prepay_id是否有效
        orderpay_rst = pay_service.getpay_by_prepayid(prepay_id)
        if not isinstance(orderpay_rst, OrderPay):
            rsp_dict['rspCode'] = orderpay_rst.get('rst_code')
            rsp_dict['rspDesc'] = orderpay_rst.get('rst_desc')
            return Response(body=MyJson.dumps(rsp_dict))
        # 2 支付订单流水不为 1-预支付
        if orderpay_rst.state != 1:
            rsp_dict['rspCode'] = 300000
            rsp_dict['rspDesc'] = '状态错误'
            return Response(body=MyJson.dumps(rsp_dict))

        # 更新订单支付流水 2-支付处理中
        upay_rst = pay_service.update_pay_by_sync(prepay_id, None, wcpay_rst)
        rsp_dict['rspCode'] = upay_rst.get('rst_code')
        rsp_dict['rspDesc'] = upay_rst.get('rst_desc')
        return Response(body=MyJson.dumps(rsp_dict))

    def notify_async(self, request):
        LOG.info('Current received message is %s' % request.json_body)
        # 微信收到商户的应答不是成功或超时，微信认为通知失败，微信会通过一定的策略定期重新发起通知，尽可能提高通知的成功率，
        # 但微信不保证通知最终能成功。 （通知频率为15/15/30/180/1800/1800/1800/1800/3600，单位：秒）

        rsp_dict = dict([('return_code', 'SUCCESS'), ('return_msg', 'OK')])

        # 1 对通知内容签名认证
        rsp_wx_dict = MyXml.parse(request.json_body)
        if rsp_wx_dict['return_code'] != 'SUCCESS':
            LOG.warn('order_notify_exception %s ' %(rsp_wx_dict['return_msg']))
            return Response(body=MyXml.gensimple(rsp_dict))
        elif rsp_wx_dict['my_sign'] != rsp_wx_dict['sign']:
            LOG.warn('order_notify_exception[SIGN_ERROR] ')
            rsp_dict['return_code'] = 'FAIL'
            rsp_dict['return_msg'] = '签名失败'
            return Response(body=MyXml.gensimple(rsp_dict))
        elif rsp_wx_dict['appid'] != CONF.wxp.appid or rsp_wx_dict['mch_id'] != CONF.wxp.mch_id:
            LOG.error('order_notify_exception[ff] ')
            rsp_dict['return_code'] = 'FAIL'
            rsp_dict['return_msg'] = 'appid或者mch_id不合法'
            return Response(body=MyXml.gensimple(rsp_dict))

        # 2 验证openid和out_trade_no有效性 及获取state,order_state,order_no,teach_id,pay_user_id
        pay_service = PayService()
        orderpay_rst = pay_service.getpay_by_userpayid(open_id=rsp_wx_dict['openid'], pay_id=rsp_wx_dict['out_trade_no'])
        if not isinstance(orderpay_rst, KeyedTuple):
            rsp_dict['return_code'] = 'FAIL'
            rsp_dict['return_msg'] = '未找到相关订单'
            LOG.error('order_notify_exception[NOT-FOUND] ')
            return Response(body=MyXml.gensimple(rsp_dict))

        LOG.info('orderpay_rst %s ' %(orderpay_rst.__getattribute__('teach_id')))
        if orderpay_rst.__getattribute__('state') == 3:
            LOG.warn('orderpay_rst already SUCCESS %s' %(rsp_wx_dict['out_trade_no']))
            # 已成功,直接返回
            return Response(body=MyXml.gensimple(rsp_dict))

        # 3 处理通知结果
        urst = None
        if rsp_wx_dict['result_code'] == 'SUCCESS':
            # 3.1更新流水及订单成功
            #    更改成员状态为已付款
            urst = pay_service.update_pay_by_async_success( pay_id=rsp_wx_dict['out_trade_no'],
                                                            order_no=orderpay_rst.__getattribute__('order_no'),
                                                            transaction_id=rsp_wx_dict['transaction_id'],
                                                            activity_uuid=orderpay_rst.__getattribute__('teach_id'),
                                                            user_uuid=orderpay_rst.__getattribute__('pay_user_id'))

        else:
            # 3.2 更新流水及订单失败
            urst = pay_service.update_pay_by_async_fail(pay_id=rsp_wx_dict['out_trade_no'],
                                                        order_no=orderpay_rst.__getattribute__('order_no'),
                                                        transaction_id=rsp_wx_dict['transaction_id'],
                                                        err_code=rsp_wx_dict['err_code'],
                                                        err_code_des=rsp_wx_dict['err_code_des'])
        if urst:
            LOG.warn('update_pay_by_async_success rst %s ' %(urst))
        # 4 处理结果返回给微信
        # return_code SUCCESS/FAIL
        # <xml>
        # <return_code><![CDATA[SUCCESS]]></return_code>
        # <return_msg><![CDATA[OK]]></return_msg>
        # </xml>

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyXml.gensimple(rsp_dict))

