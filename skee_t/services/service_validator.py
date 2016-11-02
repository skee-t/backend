#! -*- coding: UTF-8 -*-
import logging

__author__ = 'pluto'

LOG = logging.getLogger(__name__)


EXCEPTION_ERROR_MESSAGE = '%s must be given in arguments.'

TYPE_ERROR_MESSAGE = '%s given type_error in arguments.'


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
#
        return self._fn(self, dict_args)


class SkiResortCreateValidator(GenericValidator):

    def __init__(self, fn, *args, **kvargs):
        super(SkiResortCreateValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        super(SkiResortCreateValidator, self).__call__(dict_args)

        assert 'name' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'name\''

        return self._fn(self, dict_args)


class SkiResortListValidator(GenericValidator):

    def __init__(self, fn, *args, **kvargs):
        super(SkiResortListValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        super(SkiResortListValidator, self).__call__(dict_args)

        assert isinstance(dict_args[0],int), TYPE_ERROR_MESSAGE % dict_args[0]

        return self._fn(self, dict_args)

class FeedbackCreateValidator(GenericValidator):

    def __init__(self, fn, *args, **kvargs):
        super(FeedbackCreateValidator, self).__init__(fn, args, kvargs)

    def __call__(self, dict_args={}):
        super(FeedbackCreateValidator, self).__call__(dict_args)

        assert 'contact' in dict_args, EXCEPTION_ERROR_MESSAGE % '\'contact\''
        #
        return self._fn(self, dict_args)
