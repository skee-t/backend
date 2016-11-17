#! -*- coding: UTF-8 -*-

import logging

from skee_t.db.models import SpToken, Msg
from skee_t.services.service_msg import MsgService
from skee_t.services.service_sp import SpService
from skee_t.utils.my_sms import SMS
from skee_t.utils.u import U

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizMsgV1(object):

    def __init__(self):
        pass

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
