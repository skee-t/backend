#! -*- coding: UTF-8 -*-
import logging
from lycosidae.conf import CONF

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
        assert 'creator' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'creator\''
        assert 'create_time' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'create_time\''
        assert 'updater' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'updater\''
        assert 'update_time', EXCEPTION_ERROR_MESSAGE % '\'update_time\''


class NetworkCreateValidator(GenericValidator):

    def __init__(self, fn, *args, **kvargs):
        super(NetworkCreateValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        super(NetworkCreateValidator, self).__call__(dict_args)

        assert 'dc_uuid' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'dc_uuid\''
        assert 'cabinet_uuid' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'cabinet_uuid\''
        assert 'start_u_index' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'start_u_index\''
        assert 'end_u_index' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'end_u_index\''
        assert 'ip' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'ip\''

        if 'community' not in dict_args:
            dict_args['community'] = CONF.default.community

        self._fn(dict_args)


