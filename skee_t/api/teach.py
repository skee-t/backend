#! -*- coding: UTF-8 -*-
import logging

from sqlalchemy.util import KeyedTuple
from webob import Response

from skee_t.bizs.biz_teach import BizTeachV1
from skee_t.db.models import User, Level
from skee_t.db.wrappers import ActivityWrapper, MemberWrapper, MemberEstimateWrapper
from skee_t.services.service_activity import ActivityService
from skee_t.services.service_skiResort import SkiResortService
from skee_t.services.service_teach import MemberService
from skee_t.services.services import UserService
from skee_t.utils.my_json import MyJson
from skee_t.wsgi import Resource
from skee_t.wsgi import Router

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class TeachApi_V1(Router):

    def __init__(self, mapper):
        super(TeachApi_V1, self).__init__(mapper)
        controller_v1 = ControllerV1()
        mapper.connect('/',
                       controller=Resource(controller_v1),
                       action='add_teach',
                       conditions={'method': ['POST']})
        # 获取指定用户教活动
        mapper.connect('/t/{openId}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_teach_somebody',
                       conditions={'method': ['GET']})

        # 获取指定用户学活动
        mapper.connect('/l/{openId}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_learn_somebody',
                       conditions={'method': ['GET']})

        # 获取指定教学活动
        mapper.connect('/a/{teachId}',
                       controller=Resource(controller_v1),
                       action='detail_teach',
                       conditions={'method': ['GET']})

        # 获取所有教学活动
        mapper.connect('/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='list_teach',
                       conditions={'method': ['GET']})
        # 教学小队详情
        mapper.connect('/team/{teachId}/{browseOpenId}',
                       controller=Resource(controller_v1),
                       action='detail_teach_team',
                       conditions={'method': ['GET']})
        mapper.connect('/memberApply',
                       controller=Resource(controller_v1),
                       action='member_apply',
                       conditions={'method': ['POST']})
        mapper.connect('/memberApply/{teachId}/{leaderOpenId}',
                       controller=Resource(controller_v1),
                       action='list_member_apply',
                       conditions={'method': ['GET']})
        mapper.connect('/memberApprove',
                       controller=Resource(controller_v1),
                       action='member_approve',
                       conditions={'method': ['POST']})
        mapper.connect('/memberReject',
                       controller=Resource(controller_v1),
                       action='member_reject',
                       conditions={'method': ['POST']})
        # 教学小队学员列表
        mapper.connect('/member/{teachId}/{leaderOpenId}',
                       controller=Resource(controller_v1),
                       action='list_member',
                       conditions={'method': ['GET']})

        # 待晋级教学小队学员列表
        mapper.connect('/member/wp/{teachId}/{leaderOpenId}',
                       controller=Resource(controller_v1),
                       action='list_member_wait_promotion',
                       conditions={'method': ['GET']})

        # 队长给成员晋级
        mapper.connect('/memberPromotion',
                       controller=Resource(controller_v1),
                       action='member_promotion',
                       conditions={'method': ['POST']})

        # 成员给队长评价
        mapper.connect('/memberEstimate',
                       controller=Resource(controller_v1),
                       action='member_estimate',
                       conditions={'method': ['POST']})

        # 成员未评价活动
        mapper.connect('/unEstimate/{openId}/{pageIndex}',
                       controller=Resource(controller_v1),
                       action='un_estimate',
                       conditions={'method': ['GET']})

        # 活动所有评价
        mapper.connect('/estimate/{teachId}',
                       controller=Resource(controller_v1),
                       action='list_estimate',
                       conditions={'method': ['GET']})

        mapper.connect('/estimate/{teachId}/{openId}',
                       controller=Resource(controller_v1),
                       action='list_estimate',
                       conditions={'method': ['GET']})


class ControllerV1(object):

    def __init__(self):
        pass

    def add_teach(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # todo 获取当前用户
        user = UserService().get_user(req_json.get('openId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))
        else:
            req_json['creator'] = user.uuid
            req_json['type'] = 1

        # 获取雪场信息
        ski_resort = SkiResortService().list_skiResort(uuid=req_json.get('skiResortId'))
        if not isinstance(ski_resort, KeyedTuple):
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '雪场不存在'
        else:
            # 增加活动
            rst = ActivityService().create_activity(req_json)
            if rst['rst_code'] == 0:
                # 增加活动成员(队长状态为4)
                add_member_rst = MemberService().add_member(rst['uuid'], req_json['creator'], 4)
                if not add_member_rst:
                    rst['rst_code'] = add_member_rst['rst_code']
                    rst['rst_desc'] = add_member_rst['rst_desc']

            LOG.info('The result of create user information is %s' % rst)
            rsp_dict['rspCode'] = rst.get('rst_code')
            rsp_dict['rspDesc'] = rst.get('rst_desc')

        return Response(body=MyJson.dumps(rsp_dict))

    def detail_teach(self, request, teachId):
        # todo 获取当前用户所在城市
        print 'detail_teach teachId:%s' % teachId

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        item_teach = ActivityService().list_skiResort_activity(type=1, teach_id=teachId)
        if isinstance(item_teach, KeyedTuple):
            rst = ActivityWrapper(item_teach)
            rsp_dict['teaching'] = rst
        else:
            rsp_dict['rspCode'] = item_teach['rst_code']
            rsp_dict['rspDesc'] = item_teach['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    def list_teach(self, request, leaderId=None, pageIndex=None):
        #todo 获取当前用户所在城市
        print 'list_activity_teach page_index:%s' % pageIndex

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        rst = ActivityService().list_skiResort_activity(type=1, leader_id=leaderId, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['activitys'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def un_estimate(self, request, openId, pageIndex):
        print 'un_estimate page_index:%s' % pageIndex

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # todo 获取当前用户
        user = UserService().get_user(openId)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        rst = ActivityService().list_skiResort_activity(type=1, member_id_un_estimate=user.uuid, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['teachings'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))


    def list_teach_somebody(self, request, openId, pageIndex):
        print 'list_activity_myteach page_index:%s' % pageIndex
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        user_service = UserService()
        user = user_service.get_user(open_id=openId)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        # todo 更具当前教学等级,产生有趣的鼓励语
        level_info = user_service.get_level(0, user.teach_level)
        if isinstance(level_info, Level):
            rsp_dict['teachLevel'] = level_info.level_desc
            rsp_dict['encouragement'] = level_info.comment
        else:
            rsp_dict['teachLevel'] = user.teach_level
            rsp_dict['encouragement'] = '想象着桃李满天下的场景~你是否会然一笑~'

        rst = ActivityService().list_skiResort_activity(type=1, leader_id=user.uuid, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['activitys'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))

    def list_learn_somebody(self, request, openId, pageIndex):
        print 'list_learn_somebody page_index:%s' % pageIndex
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # 获取当前用户信息
        user_service = UserService()
        user_info = user_service.get_user(open_id=openId)
        if isinstance(user_info, User):
            level_info = user_service.get_level(user_info.ski_type, user_info.ski_level)
            rsp_dict['skiLevel'] = user_info.ski_level
            # todo 获取当前等级与下一级差距,个性化生产鼓励语
            if isinstance(level_info, Level):
                rsp_dict['encouragement'] = level_info.comment
            else:
                rsp_dict['encouragement'] = '加油~你是滑的最慢的~'
        else:
            rsp_dict['rspCode'] = user_info['rst_code']
            rsp_dict['rspDesc'] = user_info['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        rst = ActivityService().list_skiResort_activity(type=1, member_id_join=user_info.uuid, page_index=pageIndex)
        if isinstance(rst, list):
            rst = [ActivityWrapper(item) for item in rst]
            rsp_dict['activitys'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))

    def detail_teach_team(self, request, teachId, browseOpenId):
        LOG.info('detail_teach_team teachId:%s openId:%s' % (teachId, browseOpenId))

        # 活动教学活动详情及成员列表(包含申请中)
        rsp_dict = BizTeachV1().detail_teach_team(teachId=teachId,
                                                  memberStates=[0,1,2,3,4],
                                                  browseOpenId=browseOpenId)

        # 判断当前浏览用户是否可以参加该活动
        #  2 已被批准 1 可以加入 0 申请中等待批准
        can_join = 1
        apply_num = 0
        user = UserService().get_user(browseOpenId)
        if isinstance(user, User):
            for member in rsp_dict['members']:
                if member['id'] == user.uuid:
                    if member['state'] == 0:
                        can_join = 0
                    else:
                        can_join = 2

        # 移除申请中队员
        for i in range(len(rsp_dict['members'])-1,-1,-1):         #倒序
            if rsp_dict['members'][i]['state'] == 0:
                apply_num += 1
                del rsp_dict['members'][i]

        rsp_dict['canJoin'] = can_join
        rsp_dict['applyNum'] = apply_num
        LOG.info('The result of create user information is %s' % rsp_dict)
        return Response(body=MyJson.dumps(rsp_dict))

    def list_member(self, request, teachId, leaderOpenId):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        user = UserService().get_user(leaderOpenId)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        rsp_dict = BizTeachV1().detail_teach_team(teachId=teachId, leaderId=user.uuid)
        return Response(body=MyJson.dumps(rsp_dict))

    def list_member_wait_promotion(self, request, teachId, leaderOpenId):
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        user = UserService().get_user(leaderOpenId)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        # 成员状态: 2-已付款 活动状态: 3-已结束
        rsp_dict = BizTeachV1().detail_teach_team(teachId=teachId, leaderId=user.uuid, memberStates = [2], activityState=3)
        return Response(body=MyJson.dumps(rsp_dict))


    def member_apply(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # todo 获取当前用户
        user = UserService().get_user(req_json.get('openId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        activity_item = ActivityService().get_activity(req_json.get('teachId'), 1)
        if not activity_item:
            rsp_dict['rspCode'] = 100001
            rsp_dict['rspDesc'] = '活动不存在'
            return Response(body=MyJson.dumps(rsp_dict))

        # 判断是否超员(总人数不超过10人)
        member_count = MemberService().member_count(req_json.get('teachId'),[4,3,2,1,0])
        if not isinstance(member_count, KeyedTuple):
            rsp_dict['rspCode'] = member_count['rst_code']
            rsp_dict['rspDesc'] = member_count['rst_code']
            return Response(body=MyJson.dumps(rsp_dict))

        if member_count.__getattribute__('member_count') >= 10:
            rsp_dict['rspCode'] = 100003
            rsp_dict['rspDesc'] = '此活动太火爆,申请人过多,请选择其他活动或者稍后再试'
            return Response(body=MyJson.dumps(rsp_dict))

        member_item = MemberService().add_member(req_json.get('teachId'), user.uuid)

        if member_item['rst_code'] != 0:
            rsp_dict['rspCode'] = member_item['rst_code']
            rsp_dict['rspDesc'] = member_item['rst_desc']
        return Response(body=MyJson.dumps(rsp_dict))

    def list_member_apply(self, request, teachId, leaderOpenId):
        LOG.info('Current received message is %s' % teachId)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        # todo 获取当前用户
        user = UserService().get_user(leaderOpenId)
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        activity_item = ActivityService().get_activity(teachId, 1, user.uuid)
        if not activity_item:
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '教学活动不存在'
            return Response(body=MyJson.dumps(rsp_dict))

        rsp_dict['skiResortName'] = activity_item.__getattribute__('ski_resort_name')
        rsp_dict['trailPic'] = activity_item.__getattribute__('trail_pic')

        members = MemberService().list_member(teachId, 0)
        if isinstance(members, list):
            rsp_dict['members'] = [MemberWrapper(item) for item in members]
        else:
            rsp_dict['rspCode'] = members['rst_code']
            rsp_dict['rspDesc'] = members['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))

    def member_approve(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # todo 获取当前用户
        user = UserService().get_user(req_json.get('leaderOpenId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        activity_item = ActivityService().get_activity(req_json.get('teachId'), 1, user.uuid)
        if not activity_item:
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '教学活动不存在'
            return Response(body=MyJson.dumps(rsp_dict))

        # 判断是否超员
        member_count = MemberService().member_count(req_json.get('teachId'),[4,3,2,1])
        if not isinstance(member_count, KeyedTuple):
            rsp_dict['rspCode'] = member_count['rst_code']
            rsp_dict['rspDesc'] = member_count['rst_code']
            return Response(body=MyJson.dumps(rsp_dict))

        if member_count.__getattribute__('member_count') + req_json.get('members').__len__() > 6:
            rsp_dict['rspCode'] = '100002'
            rsp_dict['rspDesc'] = '小队成员数超过6人，请三思~'
            return Response(body=MyJson.dumps(rsp_dict))

        # 批准入队
        approve_rst = MemberService().member_update(req_json.get('teachId'), req_json.get('members'), 1)
        if approve_rst:
            rsp_dict['rspCode'] = approve_rst['rst_code']
            rsp_dict['rspDesc'] = approve_rst['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))

    def member_reject(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # todo 获取当前用户
        user = UserService().get_user(req_json.get('leaderOpenId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        activity_item = ActivityService().get_activity(req_json.get('teachId'), 1, user.uuid)
        if not activity_item:
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '教学活动不存在'
            return Response(body=MyJson.dumps(rsp_dict))

        approve_rst = MemberService().member_update(req_json.get('teachId'), req_json.get('members'), -1)
        if approve_rst:
            rsp_dict['rspCode'] = approve_rst['rst_code']
            rsp_dict['rspDesc'] = approve_rst['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))

    def member_promotion(self, request):
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        user = UserService().get_user(req_json.get('leaderOpenId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        activityService = ActivityService()
        # 活动类型:1-教学,状态:3-已结束
        activity_item = activityService.get_activity(req_json.get('teachId'), 1, user.uuid, state=3)
        if not activity_item:
            rsp_dict['rspCode'] = '100001'
            rsp_dict['rspDesc'] = '教学活动不存在或者状态不正确'
            return Response(body=MyJson.dumps(rsp_dict))

        # 更新活动成员状态
        approve_rst = MemberService().member_update(req_json.get('teachId'), req_json.get('members'), 3)
        if approve_rst:
            rsp_dict['rspCode'] = approve_rst['rst_code']
            rsp_dict['rspDesc'] = approve_rst['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        # 更新用户状态 增加用户等级变化信息
        update_rst = UserService().level_update(req_json.get('teachId'), req_json.get('members'))
        if update_rst:
            rsp_dict['rspCode'] = update_rst['rst_code']
            rsp_dict['rspDesc'] = update_rst['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        # 更新活动状态(由3结束->4学员已晋级)
        update_rst = activityService.update(req_json.get('teachId'), 3, 4, user.uuid)
        if update_rst:
            rsp_dict['rspCode'] = update_rst['rst_code']
            rsp_dict['rspDesc'] = update_rst['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        return Response(body=MyJson.dumps(rsp_dict))

    def member_estimate(self, request):
        # todo 获取当前用户
        req_json = request.json_body
        LOG.info('Current received message is %s' % req_json)

        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])

        user = UserService().get_user(req_json.get('openId'))
        if not isinstance(user, User):
            rsp_dict['rspCode'] = user['rst_code']
            rsp_dict['rspDesc'] = user['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        req_json['userId'] = user.uuid


        # 更新成员评价
        approve_rst = MemberService().member_estimate(req_json)
        if approve_rst['rst_code'] != 0:
            rsp_dict['rspCode'] = approve_rst['rst_code']
            rsp_dict['rspDesc'] = approve_rst['rst_desc']
            return Response(body=MyJson.dumps(rsp_dict))

        return Response(body=MyJson.dumps(rsp_dict))

    def list_estimate(self, request, teachId, openId=None):
        print 'list_estimate page_index:%s' % teachId
        rsp_dict = dict([('rspCode', 0), ('rspDesc', 'success')])
        # 通过openId获取用户信息
        userId = None
        if openId:
            user = UserService().get_user(openId)
            if not isinstance(user, User):
                rsp_dict['rspCode'] = user['rst_code']
                rsp_dict['rspDesc'] = user['rst_desc']
                return Response(body=MyJson.dumps(rsp_dict))
            else:
                userId = user.uuid

        teach_info = ActivityService().list_skiResort_activity(type=1, teach_id=teachId)
        if isinstance(teach_info, KeyedTuple):
            rsp_dict['teaching'] = ActivityWrapper(teach_info)
        else:
            rsp_dict['rspCode'] = teach_info['rst_code']
            rsp_dict['rspDesc'] = teach_info['rst_desc']

        rst = MemberService().list_estimate(teach_id=teachId, user_id=userId)
        if isinstance(rst, list):
            rst = [MemberEstimateWrapper(item) for item in rst]
            rsp_dict['estimates'] = rst
        else:
            rsp_dict['rspCode'] = rst['rst_code']
            rsp_dict['rspDesc'] = rst['rst_desc']

        return Response(body=MyJson.dumps(rsp_dict))