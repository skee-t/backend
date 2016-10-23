#! -*- coding: utf-8 -*-
from oslo_config import cfg

__author__ = 'pluto'


DEFAULTS_OPTS = [
    cfg.BoolOpt('debug', default=False, help='Whether debug or not'),

    cfg.StrOpt('user_appliance', default='skis', help='The appliance which user wonted.'),
    cfg.StrOpt('user_image_path', default='', help='The default path of user image.'),
]

DB_OPTS = [
    cfg.StrOpt('db_type', default='mysql', help=''),
    cfg.StrOpt('driver', default='mysqlconnector', help=''),
    cfg.StrOpt('host', default='0.0.0.0', help='The url of database'),
    cfg.StrOpt('port', default='3306', help='The port which the database instance listen'),
    cfg.StrOpt('database', default='skee_t', help='The logic name of the database instance'),
    cfg.StrOpt('username', default='root', help='The username of database'),
    cfg.StrOpt('password', default='root', help='The password of database'),
    cfg.StrOpt('encoding', default='UTF-8', help=''),
    cfg.BoolOpt('debug', default=False, help=''),
    cfg.IntOpt('max_pool_size', default=10, help='The number of connection pool which client connect to the database'),
    cfg.IntOpt('idle_timeout', default=3600, help='The pool to recycle connections after the given number of seconds has passed. It defaults to -1, or no timeout.'),
    cfg.IntOpt('max_overflow', default=0, help=''),
    cfg.IntOpt('pool_timeout', default=30, help='The number of seconds to wait before giving up on getting a connection from the pool'),
]

QUEUE_OPTS = [
    cfg.StrOpt('driver', default='', help=''),
    cfg.StrOpt(''),
]

WSGI_OPTS = [
    cfg.StrOpt('config', default='/etc/skee_t/paste/skee_t.ini', help=''),
    cfg.StrOpt('host', default='0.0.0.0', help=''),
    cfg.IntOpt('port', default=8080, help=''),
]

DEFAULTS_GROUP = cfg.OptGroup('default', 'default', help='')

DB_GROUP = cfg.OptGroup('database', 'database', help='')

WSGI_GROUP = cfg.OptGroup('wsgi', 'wsgi', help='')

CONF = cfg.CONF

CONF.register_group(DB_GROUP)
CONF.register_opts(DB_OPTS, DB_GROUP)

CONF.register_group(WSGI_GROUP)
CONF.register_opts(WSGI_OPTS, WSGI_GROUP)

CONF.register_group(DEFAULTS_GROUP)
CONF.register_opts(DEFAULTS_OPTS, DEFAULTS_GROUP)

CLI_ARGS = [
    cfg.StrOpt('action', default='start', required=True, help='The action of command skee_t'),
    cfg.StrOpt('sock_file', default='/tmp/skee_t.sock', help='The socket file of skee_t'),
    cfg.StrOpt('pid_file', default='/tmp/skee_t.pid', help='The pid file of skee_t'),
    cfg.StrOpt('log_config', default='/etc/skee_t/skee_t_logging.conf', help='The config file of logging'),
]
CONF.register_cli_opts(CLI_ARGS)
