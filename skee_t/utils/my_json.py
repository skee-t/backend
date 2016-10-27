#! -*- coding: UTF-8 -*-
import json

__author__ = 'rensikun'


class MyJson:

    @staticmethod
    def dumps(rsp_dict):
        return json.dumps(rsp_dict, ensure_ascii=False, sort_keys=True)

