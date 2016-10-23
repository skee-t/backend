#! -*- coding: UTF-8 -*-
import logging
from skee_t.conf import CONF

__author__ = 'pluto'

LOG = logging.getLogger(__name__)


EXCEPTION_ERROR_MESSAGE = '%s must be given in arguments.'


class Validator(object):

    def __init__(self, fn, *args, **kvargs):
        self._fn = fn


class GenericValidator(Validator):

    def __init__(self, fn, *args, **kvargs):
        super(GenericValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        assert dict_args is not None, 'The argument is none, expect a dict.'


class UserCreateValidator(GenericValidator):

    def __init__(self, fn, *args, **kvargs):
        super(UserCreateValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        super(UserCreateValidator, self).__call__(dict_args)

        assert 'name' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'name\''

        self._fn(dict_args)


