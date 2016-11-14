#! -*- coding: UTF-8 -*-
import hashlib
import logging

from webob import Response

from skee_t.wsgi import Resource
from skee_t.wsgi import Router
from skee_t.wxservices import receive
from skee_t.wxservices import reply

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
        # mapper.connect('/delete/{id}',
        #                controller=wsgi.Resource(controller_v1),
        #                action='delete',
        #                conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

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
        LOG.info('Current received message is %s' % request.json_body)
        try:
            # 非 json
            recMsg = receive.parse_xml(request.json_body)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                content = "test"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                LOG.info("replay-msg %s " % replyMsg)
                return replyMsg.send()
            else:
                LOG.info("do-not-process")
                return "success"
        except Exception, Argment:
            return Argment
