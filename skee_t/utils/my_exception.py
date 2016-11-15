#! -*- coding: UTF-8 -*-

__author__ = 'rensikun'


class MyException(Exception):

    def __init__(self, code, desc):
        Exception.__init__(self)
        self.code = code
        self.desc = desc