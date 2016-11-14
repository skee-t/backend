#! -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from skee_t.conf import CONF

__author__ = 'pluto'


def create_engine(connection, idle_timeout=3600, max_pool_size=10, max_overflow=10,
                  pool_timeout=30, encoding='UTF-8', debug=False):
    """
    A function which represents create a database connection engine
    :param connection:
    :param idle_timeout:
    :param max_pool_size:
    :param max_overflow:
    :param pool_timeout:
    :param encoding:
    :param debug:
    :return:
    """
    db_url = make_url(connection)

    _init_engine_arguments = {'pool_recycle': idle_timeout,
                              'pool_size': max_pool_size,
                              'max_overflow': max_overflow,
                              'pool_timeout': pool_timeout,
                              'encoding': encoding,
                              'echo': debug,
                              'case_sensitive': True}

    engine = sqlalchemy.create_engine(db_url, **_init_engine_arguments)
    return engine


MYSQL_DB_URL = '%(db_type)s+%(driver)s://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s'


def engine_single(cls, db_url=None, idle_timeout=3600, max_pool_size=10,
                  max_overflow=0, pool_timeout=30, encoding='UTF-8', debug=False):
    __instances = dict()

    def get_instance():
        if cls not in __instances:
            __instances[cls] = cls(db_url=db_url,
                                   idle_timeout=idle_timeout,
                                   max_pool_size=max_pool_size,
                                   max_overflow=max_overflow,
                                   pool_timeout=pool_timeout,
                                   encoding=encoding,
                                   debug=debug)
        return __instances[cls]

    return get_instance()


class DbEngine(object):
    """
    A class which represents database connection engine.This class is a singleton class.

    .. attribute:: engine
        SQLAlchemy engine instance
    .. attribute:: session_maker
        SQLAlchemy session instance
    """
    def __init__(self, db_url=None, idle_timeout=3600, max_pool_size=10,
                 max_overflow=0, pool_timeout=30, encoding='UTF-8', debug=False):
        self._db_url = db_url
        self._engine = create_engine(db_url,
                                     idle_timeout,
                                     max_pool_size,
                                     max_overflow,
                                     pool_timeout,
                                     encoding,
                                     debug)
        self._session_maker = sessionmaker(bind=self._engine)

    def get_db_url(self):
        return self._db_url

    def get_engine(self):
        return self._engine

    def get_session(self, autocommit=True, expire_on_commit=False):
        return self._session_maker(autocommit=autocommit,
                                   expire_on_commit=expire_on_commit)

    @classmethod
    def get_session_simple(cls):
        return DbEngine.get_single().get_session(autocommit=False, expire_on_commit=True)

    @classmethod
    def get_single(cls):
        if not hasattr(cls, '_inst'):
            cls._inst = DbEngine.get_instance()
        return cls._inst

    @classmethod
    def get_instance(cls):
        """
        Get a instance of DBEngine
        :return: DBEngine instance
        """
        return cls(MYSQL_DB_URL % {'db_type': CONF.database.db_type,
                                      'driver': CONF.database.driver,
                                      'username': CONF.database.username,
                                      'password': CONF.database.password,
                                      'host': CONF.database.host,
                                      'port': CONF.database.port,
                                      'database': CONF.database.database},
                      CONF.database.idle_timeout,
                      CONF.database.max_pool_size,
                      CONF.database.max_overflow,
                      CONF.database.pool_timeout,
                      CONF.database.encoding,
                      CONF.database.debug)