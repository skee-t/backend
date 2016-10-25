#! -*-coding:UTF-8 -*-
import abc

__author__ = 'pluto'


class AbstractORMWrapper(dict):

    def __init__(self, model_obj):
        print self._getClass()
        if isinstance(model_obj, self._getClass()):
            for attr in self._getwrapattrs():
                self[attr] = model_obj.__getattribute__(attr).__str__()

    @abc.abstractmethod
    def _getClass(self):
        pass

    @abc.abstractmethod
    def _getwrapattrs(self):
        pass

