#! -*-coding:UTF-8 -*-
import abc

from skee_t.db.models import SkiResort

__author__ = 'pluto'


class AbstractORMWrapper(dict):

    def __init__(self, model_obj):
        print self._getClass()
        if isinstance(model_obj, self._getClass()):
            for attr in self._getwrapattrs():
                self[underline_to_camel(attr)] = model_obj.__getattribute__(attr)

    @abc.abstractmethod
    def _getClass(self):
        pass

    @abc.abstractmethod
    def _getwrapattrs(self):
        pass


class SkiResortWrapper(AbstractORMWrapper):

    def _getwrapattrs(self):
        return ['id', 'name', 'city', 'address', 'spec_pic', 'trail_pic', 'has_bus', 'contact', 'disabled', 'deleted',]

    def _getClass(self):
        return SkiResort


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