#! -*- coding: UTF-8 -*-

from wsgiref.simple_server import make_server
from paste.deploy import loadapp

author = 'pluto'

if __name__ == '__main__':
    config = 'config:%s' % '/Users/pluto/workspace/skee_t/etc/paste/skee_t.ini'
    wsgi_app = loadapp(config, 'skee_t')
    server = make_server('0.0.0.0', 8080, wsgi_app)
    server.serve_forever()
