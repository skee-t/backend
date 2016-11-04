#! -*- coding: UTF-8 -*-
import logging

__author__ = 'pluto'

LOG = logging.getLogger(__name__)


class Versions(object):

    def __init__(self, version):
        super(Versions, self).__init__()
        self._version = version

    def __call__(self, environ, start_response):
        content = ["%s\n" % self._version]
        start_response("200 OK", [("Content-type", "text/plain")])
        LOG.info('---------->Test')
        return content

    @classmethod
    def factory(cls, global_conf, **kwargs):
        return cls(kwargs['version'])

