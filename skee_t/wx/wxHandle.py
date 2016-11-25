#! -*- coding: UTF-8 -*-
import hashlib
import logging
import time

from webob import Response

from skee_t.conf import CONF
from skee_t.db.models import Property
from skee_t.services.service_system import SysService
from skee_t.utils.my_json import MyJson
from skee_t.utils.u import U
from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wx.basic import receive
from skee_t.wx.basic import reply
from skee_t.wx.basic.basic import WxBasic
from skee_t.wx.basic.jsbasic import WxJSBasic
from skee_t.wx.proxy.menu import Menu
from skee_t.wx.proxy.webAuthaccessToken import WxOpenIdProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class WxHandle_V1(Router):

    def __init__(self, mapper):
        super(WxHandle_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/msg',
                       controller=Resource(controller_v1),
                       action='get_handle',
                       conditions={'method': ['GET']})
        mapper.connect('/msg',
                       controller=Resource(controller_v1),
                       action='post_handle',
                       conditions={'method': ['POST']})
        mapper.connect('/accToken',
                       controller=Resource(controller_v1),
                       action='accToken',
                       conditions={'method': ['GET']})
        mapper.connect('/asb',
                       controller=Resource(controller_v1),
                       action='auth_snsapi_base',
                       conditions={'method': ['GET']})

        mapper.connect('/wechatjs',
                       controller=Resource(controller_v1),
                       action='wechatjs',
                       conditions={'method': ['POST']})

        mapper.connect('/menu',
                       controller=Resource(controller_v1),
                       action='menu_create',
                       conditions={'method': ['POST']})
        mapper.connect('/menu',
                       controller=Resource(controller_v1),
                       action='menu_query',
                       conditions={'method': ['GET']})
        mapper.connect('/menu',
                       controller=Resource(controller_v1),
                       action='menu_delete',
                       conditions={'method': ['DELETE']})
        mapper.connect('/menu/self',
                       controller=Resource(controller_v1),
                       action='menu_self',
                       conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    def wechatjs(self, request):
        LOG.info('wechatjs')
        try:
            back_dict = dict()
            jsapi_ticket = WxJSBasic().get_jsapi_ticket()
            LOG.info("ticket [%s] " % (jsapi_ticket))
            back_dict['nonceStr'] = U.gen_uuid()
            back_dict['jsapi_ticket'] = jsapi_ticket
            back_dict['timeStamp'] = str(int(time.time()))
            back_dict['url'] = request.json_body['url']
            back_dict['signature'] = U.sign_sha1(back_dict)

            back_dict['appId'] = CONF.wxp.appid
            back_dict['rspCode'] = 0
            back_dict['rspDesc'] = 'success'

            LOG.info("rsp  %s " % back_dict)
            return Response(body=MyJson.dumps(back_dict))
        except Exception, Argument:
            return Argument

    def get_handle(self, request):
        LOG.info('Current received message is %s' % request.params)
        try:
            signature = request.params['signature']
            if not signature:
                return "hello, this is handle view"
            timestamp = request.params['timestamp']
            nonce = request.params['nonce']
            echostr = request.params['echostr']
            token = "52a07fe3b23142289f9965ba80dac6a5" #请按照公众平台官网\基本配置中信息填写

            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            LOG.info("handle/GET func: hashcode %s, signature  %s " % (hashcode, signature))
            if hashcode == signature:
                LOG.info("return echostr: %s" % echostr)
                return Response(body=echostr)
            else:
                return ""
        except Exception, Argument:
            return Argument

    def post_handle(self, request):
        xmlRequest = request.json_body
        LOG.info('Current received message is %s' % xmlRequest)
        try:
            # 非 json
            recMsg = receive.parse_xml(xmlRequest)
            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                # if recMsg.MsgType == 'text':
                #     content = "test"
                #     replyMsg = reply.TextMsg(toUser, fromUser, content)
                #     return replyMsg.send()
                # if recMsg.MsgType == 'image':
                #     mediaId = recMsg.MediaId
                #     replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                #     return replyMsg.send()
                if recMsg.MsgType == 'event':
                    if recMsg.Event == 'subscribe':
                        property = SysService.getByKey('wx-subscribe')
                        if isinstance(property, Property):
                            content = property.value
                        else:
                            content = "欢迎您关注滑雪帮"
                        replyMsg = reply.TextMsg(toUser, fromUser, content.decode('utf-8'))
                        return Response(body=replyMsg.send())
                else:
                    # 转发至多客服系统
                    replyMsg = reply.CustomerMsg(toUser, fromUser)
                    return Response(body=replyMsg.send())
            else:
                print "non-process"
                return reply.Msg().send()

        except Exception, Argment:
            return Argment

    def accToken(self, request):
        try:
           acc_token = WxBasic().get_access_token()
           LOG.info("acc_token [%s] " % (acc_token))
           return Response(body=acc_token)
        except Exception, Argment:
            return Argment

    def auth_snsapi_base(self, request):
        LOG.info('Current received message is %s' % request.params)
        try:
            code = request.params['code']
            # state = request.params['state']
            redirect = request.params['t']

            # 通过code换取网页授权access_token
            wxWebAccessToken = WxOpenIdProxy.get_open_id(code)
            LOG.info("openid [%s] " % (wxWebAccessToken.open_id))

            # 转向目标页面
            response = Response()
            # unicode to str
            response.headers["Location"] = str('http://skihelp.cn/%s?id=%s' % (redirect, wxWebAccessToken.open_id))
            response.status_int = 302
            LOG.info("redirect [%s] " % (response.headers["Location"]))
            return response
        except Exception, Argment:
            LOG.exception("auth_snsapi_base error.")
            return Argment

    def menu_create(self, request):
        try:
            acc_token = WxBasic().get_access_token()
            rst = Menu().create(request.json_body, acc_token)
            LOG.info("menu_create_rst [%s] " % (rst))
            return Response(body=rst)
        except Exception, Argment:
            LOG.exception("menu_create error.")
            return Argment

    def menu_query(self, request):
        try:
            acc_token = WxBasic().get_access_token()
            rst = Menu().query(acc_token)
            LOG.info("menu_query_rst [%s] " % (rst))
            return Response(body=rst)
        except Exception, Argment:
            return Argment

    def menu_delete(self, request):
        try:
            acc_token = WxBasic().get_access_token()
            rst = Menu().delete(acc_token)
            LOG.info("menu_delete_rst [%s] " % (rst))
            return Response(body=rst)
        except Exception, Argment:
            return Argment

    def menu_self(self, request):
        try:
            acc_token = WxBasic().get_access_token()
            rst = Menu().get_current_selfmenu_info(acc_token)
            LOG.info("menu_delete_rst [%s] " % (rst))
            return Response(body=rst)
        except Exception, Argment:
            return Argment


