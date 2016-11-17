#! -*-coding:UTF-8 -*-
import abc
import datetime
import decimal

from sqlalchemy.util import KeyedTuple

from skee_t.db.models import SkiResort, Activity, User, ActivityMember, Msg

__author__ = 'pluto'


class AbstractORMWrapper(dict):

    def __init__(self, model_obj):
        print self._getClass()
        if isinstance(model_obj, self._getClass()) or isinstance(model_obj, KeyedTuple):
            # 将复杂类型转换为字符串
            # 将key转化为驼峰
            for attr in self._getwrapattrs():
                attr_value = model_obj.__getattribute__(attr)
                if isinstance(attr_value, decimal.Decimal):
                    self[underline_to_camel(attr)] = format(attr_value, '0.0f')
                elif isinstance(attr_value, datetime.datetime):
                    self[underline_to_camel(attr)] = attr_value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    self[underline_to_camel(attr)] = attr_value
            # 组合字段
            self._mergeattrs(model_obj)

    @abc.abstractmethod
    def _getClass(self):
        pass

    @abc.abstractmethod
    def _getwrapattrs(self):
        pass

    def _mergeattrs(self, model_obj):
        pass


class SkiResortWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'name', 'city', 'address', 'spec_pic', 'trail_pic', 'has_bus']

    def _getClass(self):
        return SkiResort

    def _mergeattrs(self, model_obj):
        self['peopleStatus'] = '%s人参与/%s人感兴趣' \
                               % (model_obj.__getattribute__('join_count'),
                                  model_obj.__getattribute__('interest_count')
                                  )


class SkiResortSimpleWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'name', 'address', 'teaching_fee']

    def _getClass(self):
        return SkiResort


class UserWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['phone_no', 'ski_level', 'ski_type', 'name', 'head_image_path']

    def _getClass(self):
        return User


class UserDetailWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['sex', 'phone_no', 'ski_level', 'ski_type', 'ski_age', 'teach_level', 'name', 'head_image_path']

    def _getClass(self):
        return User


class SkiHisWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['meeting_time', 'ski_resort_name', 'title']

    def _getClass(self):
        return str

    def _mergeattrs(self, model_obj):
        # self['skiHisStr'] = '%s %s %s' \
        #                     % (model_obj.__getattribute__('meeting_time').strftime('%Y-%m-%d'),
        #                        model_obj.__getattribute__('ski_resort_name'),
        #                        model_obj.__getattribute__('title'))
        self['skiHisStr'] = '%s %s' \
                            % (model_obj.__getattribute__('meeting_time').strftime('%Y-%m-%d'),
                               model_obj.__getattribute__('title'))


class ActivityWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'title', 'type', 'state', #'fee', 'period',
                'meeting_time','estimate',
                'leader_id', 'leader_name', 'leader_head_image_path']

    def _getClass(self):
        return Activity

    def _mergeattrs(self, model_obj):
        self['peopleStatus'] = '%s人参与/%s人感兴趣' \
                                 % (model_obj.__getattribute__('join_count'),
                                    model_obj.__getattribute__('interest_count')
                                    )
        self['feeDesc'] = '费用：%0.0f元/人 时长：%s小时' \
                               % (model_obj.__getattribute__('fee'),
                                  model_obj.__getattribute__('period')
                                  )


class ActivityDetailWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return [
            'id', 'title', 'type', 'state', 'level_limit', 'meeting_time', 'venue', 'period', 'fee', 'quota', 'notice',
            'ski_resort_id', 'ski_resort_name', 'trail_pic',
            'leader_id', 'leader_contact', ]

    def _getClass(self):
        return Activity


class MemberWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'head_image_path', 'name', 'ski_level', 'state']

    def _getClass(self):
        return ActivityMember


class MemberEstimateWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['user_id', 'user_name', 'type', 'score', 'content']

    def _getClass(self):
        return ActivityMember


class MsgWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'type', 'create_time', 'src_user_name', 'src_head_image_path', 'activity_id', 'activity_title']

    def _getClass(self):
        return Msg

def camel_to_underline(camel_format):
    """
        驼峰命名格式转下划线命名格式
    """
    underline_format=''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_'+_s_.lower()
    return underline_format


def underline_to_camel(underline_format):
    """
        下划线命名格式驼峰命名格式
    """

    #将字符串转化为list
    string_list = str(underline_format).split('_')
    first = string_list[0].lower()

    #str.capitalize():将字符串的首字母转化为大写
    others_capital = [word.capitalize() for word in string_list[1:]]
    others_capital[0:0] = [first]

    #将list组合成为字符串，中间无连接符
    return ''.join(others_capital)