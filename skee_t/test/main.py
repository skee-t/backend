#! -*- coding: UTF-8 -*-
import logging
from wsgiref.simple_server import make_server

import os
from paste.deploy import loadapp
from sqlalchemy import create_engine

from skee_t.conf import CONF
from skee_t.db import DbEngine
from skee_t.db.model_base import DB_BASE_MODEL

author = 'pluto'

APP_NAME = 'skee_t'

# 获取当前项目目录
PROJECT_DIR = os.path.abspath(__file__).replace('/skee_t/test/main.py','')
DB_CONFIG_FILE = PROJECT_DIR + '/etc/skee_t.conf'
WEB_CONFIG_FILE =  PROJECT_DIR + '/etc/paste/skee_t.ini'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    CONF(default_config_files=[DB_CONFIG_FILE])

    engine = create_engine(DbEngine.get_instance()._db_url, echo=True)
    DB_BASE_MODEL.metadata.create_all(engine)

    config = 'config:%s' % WEB_CONFIG_FILE
    wsgi_app = loadapp(config, APP_NAME)
    server = make_server('0.0.0.0', 8080, wsgi_app)
    server.serve_forever()
