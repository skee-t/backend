#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.util import KeyedTuple

from skee_t.db.wrappers import ActivityDetailWrapper, MemberWrapper
from skee_t.services.service_activity import ActivityService
from skee_t.services.service_teach import MemberService
from skee_t.services.services import UserService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class BizTeachV1(object):

    def __init__(self):
        pass

    def detail_teach_team(self, teachId, leaderId = None,
                          memberStates = [1,2,3,4],
                          activityState=None,
                          browseOpenId= None):
        service = ActivityService()

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = service.get_activity(activity_id=teachId,type=1,leader_id=leaderId,state=activityState)
        if not isinstance(rst, KeyedTuple):
            rsp_dict['rspCode'] = 100001
            rsp_dict['rspDesc'] = '教学信息不存在'
            return rsp_dict
        else:
            rst = ActivityDetailWrapper(rst)
            rsp_dict.update(rst)

        # -2：报名后退出；-1: 队长拒绝； 0：已报名待批准；1：队长批准待付款; 2: 已付款 3:晋级 4:队长
        members = MemberService().list_member(teachId, memberStates, leaderId)
        if isinstance(members, list):
            rsp_dict['members'] = [MemberWrapper(item) for item in members]
        else:
            rsp_dict['rspCode'] = members['rst_code']
            rsp_dict['rspDesc'] = members['rst_desc']

        # 记录用户事件
        if browseOpenId:
            UserService().add_user_event(browseOpenId, teachId)

        return rsp_dict

    def check_user_activity_membercount(self, teachId, openId, memberStates):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # # todo 获取当前用户
        # user = UserService().get_user(openId)
        # if not isinstance(user, User):
        #     rsp_dict['rspCode'] = user['rst_code']
        #     rsp_dict['rspDesc'] = user['rst_desc']
        #     return rsp_dict
        #
        # activity_item = ActivityService().get_activity(teachId, 1)
        # if not activity_item:
        #     rsp_dict['rspCode'] = 100001
        #     rsp_dict['rspDesc'] = '活动不存在'
        #     return rsp_dict
        #
        # # 判断是否超员(总人数不超过10人)
        # member_count = MemberService().member_count(teachId,memberStates)
        # if not isinstance(member_count, KeyedTuple):
        #     rsp_dict['rspCode'] = member_count['rst_code']
        #     rsp_dict['rspDesc'] = member_count['rst_code']
        #     return rsp_dict

