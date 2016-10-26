#! -*-coding:UTF-8 -*-
import abc

from skee_t.db.models import SkiResort

__author__ = 'pluto'


class AbstractORMWrapper(dict):

    def __init__(self, model_obj):
        print self._getClass()
        if isinstance(model_obj, self._getClass()):
            for attr in self._getwrapattrs():
                self[attr] = model_obj.__getattribute__(attr)

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
