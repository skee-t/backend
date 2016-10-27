#! -*- coding: UTF-8 -*-

import json

__author__ = 'rensikun'


class MyJson:
    def __init__(self):
        pass

    @staticmethod
    def dumps(rsp_dict):
        return json.dumps(rsp_dict, ensure_ascii=False, sort_keys=True)

