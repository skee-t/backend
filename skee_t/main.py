#! -*- coding:utf-8 -*-
import logging
import logging.config
import sys
from wsgiref.simple_server import make_server
from paste.deploy import loadapp
from skee_t.conf import CONF
from skee_t.launcher import Launcher

__author__ = 'pluto'


DEFAULT_CONFIG_FILES = '/etc/skee_t/skee_t.conf'
APP_NAME = 'skee_t'

LOG = logging.getLogger(__name__)


class Lycosidae(Launcher):

    __server = None

    def _run(self):
        config = 'config:%s' % CONF.wsgi.config
        wsgi_app = loadapp(config, APP_NAME)
        self.__server = make_server(CONF.wsgi.host, CONF.wsgi.port, wsgi_app)
        self.__server.serve_forever()
        LOG.info('The wsgi server has been started.')

    def _pre_close(self):
        if self.__server is not None:
            self.__server.server_close()
            self.__server = None


def main():
    print sys.argv[1:]
    CONF(sys.argv[1:], default_config_files=DEFAULT_CONFIG_FILES)
    logging.config.fileConfig(CONF.log_config)

    if CONF.default.debug is True:
        logging.basicConfig(level=logging.DEBUG)

    if CONF.action == 'start':
        launcher = Lycosidae()
        launcher.start()
    else:
        Launcher.stop()
