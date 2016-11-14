#! -*- coding: UTF-8 -*-
import logging.config
import sys
from wsgiref.simple_server import make_server

import os
from paste.deploy import loadapp

from skee_t.conf import CONF

author = 'pluto'

APP_NAME = 'skee_t'

# 获取当前项目目录
PROJECT_DIR = os.path.abspath(__file__).replace('/skee_t/test/main.py','')
DB_CONFIG_FILE = PROJECT_DIR + '/etc/skee_t.conf'
WEB_CONFIG_FILE = PROJECT_DIR + '/etc/paste/skee_t.ini'
LOG_CONFIG_FILE = PROJECT_DIR + '/etc/skee_t_logging.conf'

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    logging.basicConfig(level=logging.DEBUG,stream=sys.stderr)
    # logging.config.fileConfig(LOG_CONFIG_FILE)    # 采用配置文件
    CONF(default_config_files=[DB_CONFIG_FILE])

    config = 'config:%s' % WEB_CONFIG_FILE
    wsgi_app = loadapp(config, APP_NAME)
    server = make_server('0.0.0.0', 8080, wsgi_app)
    server.serve_forever()
