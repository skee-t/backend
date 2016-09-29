#! -*- coding: UTF-8 -*-
from requests import Response
import webob

__author__ = 'pluto'


class Versions(object):

    def __init__(self, version):
        super(Versions, self).__init__()
        self._version = version

    def __call__(self, environ, start_response):
        content = ["%s\n" % self._version]
        start_response("200 OK", [("Content-type", "text/plain")])
        print "---------->Test"
        return content

    @classmethod
    def factory(cls, global_conf, **kwargs):
        return cls(kwargs['version'])

