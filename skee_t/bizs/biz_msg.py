#! -*- coding: UTF-8 -*-

import logging

from skee_t.db.models import SpToken, Msg, Property
from skee_t.services.service_msg import MsgService
from skee_t.services.service_sp import SpService
from skee_t.services.service_system import SysService
from skee_t.utils.my_json import MyJson
from skee_t.utils.my_sms import SMS
from skee_t.utils.u import U
from skee_t.wx.basic.basic import WxBasic
from skee_t.wx.proxy.templateMsg import WxTempMsgProxy

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizMsgV1(object):

    def __init__(self):
        pass

    def notify_wx_temp_msg(self, type, source_id, source_name, target_open_id,
                           target_id, target_name, activity_id, activity_title = None):

        # 消息类型:
        # 0系统通知 1成员入队提醒; 2批准入队通知; 3评价队长提醒;
        # 4成员评价通知; 5 学员评级提醒; 6 学员晋级通知; 7 成员退出通知
        if type == 1:
           pass
        elif type == 2:
            # {{first.DATA}}
            # 您的队伍：{{keyword1.DATA}}
            # 处理时间：{{keyword2.DATA}}
            # {{remark.DATA}}
            # 亲爱的蔚小春，大神【叨叨】已经批准你入队
            # 您的队伍：【美林谷·单板】雪乐缘叨叨提高班
            # 处理时间： 2016-03-01 17:51
            # 还差一步就能得到TA的指点。点击查看详情。
            send_msg_template = None
            property = SysService.getByKey('wx-notify-approve')
            if isinstance(property, Property):
                send_msg_template = property.value

            send_msg = send_msg_template % {'target_name':target_name,'source_name':source_name,
                                            'activity_title':activity_title,'cur_time':U.timeStr(),
                                            'template_id': 'ySPCCRtPJJaoI28o_DHIdCVeHWfijAofF0_W0xDUSHU',
                                            'activity_id':activity_id ,'target_open_id':target_open_id}
        elif type == 3:
            pass
        elif type == 4:
            pass
        elif type == 5:
            pass
        elif type == 6:
            pass
        elif type == 7:  # 成员退出通知
            send_msg_template = None
            property = SysService.getByKey('wx-notify-quit')
            if isinstance(property, Property):
                send_msg_template = property.value

            send_msg = send_msg_template % {'target_name':target_name,'source_name':source_name,
                                            'activity_title':activity_title,'cur_time':U.timeStr(),
                                            'template_id': 'ySPCCRtPJJaoI28o_DHIdCVeHWfijAofF0_W0xDUSHU',
                                            'activity_id':activity_id ,'target_open_id':target_open_id}

        acc_token = WxBasic().get_access_token()
        wxRsp = WxTempMsgProxy().send(acc_token,msg=str(send_msg))

        # 消息入库
        msg = Msg(uuid=U.gen_uuid(), type=type, source_id=source_id,
                  target_id=target_id,
                  activity_id=activity_id)
        msg.state = 1 if wxRsp['errcode'] == 0 else 0
        MsgService().create(msg)

    def create_with_send_sms(self, type, source_id, source_name,
                             target_id, target_name, target_phone, activity_id):
        LOG.info('BizMsgV1 param is %s' % target_phone)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # 消息类型:
        # 0系统通知 1成员入队提醒; 2批准入队通知; 3评价队长提醒;
        # 4成员评价通知; 5 学员评级提醒; 6 学员晋级通知

        # 消息短信通知
        send_rst = None
        if type == 1:
            send_rst = SMS.send_notify_apply(target_phone,
                                         target_name, source_name)
        elif type == 2:
            send_rst = SMS.send_notify_approve(target_phone,
                                 target_name, source_name)
        elif type == 3:
            send_rst = SMS.send_notify_stu_commit(target_phone,
                                               target_name, source_name)
        elif type == 4:
            send_rst = SMS.send_notify_tea_commit(target_phone,
                                                  target_name, source_name)
        elif type == 5:
            send_rst = SMS.send_notify_tea_pro(target_phone,
                                                  target_name, source_name)
        elif type == 6:
            send_rst = SMS.send_notify_stu_pro(target_phone,
                                            target_name, source_name)

        LOG.info('send_notify rst is %s' % send_rst)
        uuid = U.gen_uuid()
        # 记录短信
        sp_token = SpToken(
            token=uuid,
            phone_no=target_phone,
            auth_code='notify',
            template_code=send_rst['template_code'],
            state=0 if (int(send_rst['rst_code'])) == 0 else -1,
            request_id=send_rst['request_id']
        )
        csp = SpService().create_sp(sp_token, -1)
        LOG.info('create_sp rst is %s' % csp)

        # 消息入库
        # 创建 成员入队提醒
        msg = Msg(uuid=U.gen_uuid(), type=type, source_id=source_id,
                  target_id=target_id,
                  activity_id=activity_id)
        msg.state = 1 if (int(send_rst['rst_code'])) == 0 else 0
        MsgService().create(msg)