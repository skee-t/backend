#! -*- coding: UTF-8 -*-

import random

__author__ = 'rensikun'


class U:
    def __init__(self):
        pass

    @staticmethod
    def gen_auth_code_num():
        code_list = []
        for i in range(6):
            random_num = random.randint(0, 9) # 随机生成0-9的数字
            code_list.append(str(random_num))
        verification_code = ''.join(code_list)
        return verification_code

    @staticmethod
    def gen_auth_code():
        code_list = []
        for i in range(2):
            random_num = random.randint(0, 9) # 随机生成0-9的数字
            # 利用random.randint()函数生成一个随机整数a，使得65<=a<=90
            # 对应从“A”到“Z”的ASCII码
            a = random.randint(65, 90)
            b = random.randint(97, 122)
            random_uppercase_letter = chr(a)
            random_lowercase_letter = chr(b)
            code_list.append(str(random_num))
            code_list.append(random_uppercase_letter)
            code_list.append(random_lowercase_letter)
        verification_code = ''.join(code_list)
        return verification_code

