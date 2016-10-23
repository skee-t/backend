#! -*- coding: UTF-8 -*-
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import now

__author__ = 'pluto'


class SkeeTDbBaseModel(object):

    @declared_attr
    def __tablename__(cls):
        return '%ss' % cls.__name__.lower()


DB_BASE_MODEL = declarative_base(cls=SkeeTDbBaseModel)


class GenericModel(object):
    """
    The basic model object of the Skee_T backend project.
    This is parent model of the persistent objects.
    .. attribute:: create_time
        The datetime of record when be created.
    .. attribute:: creator:
        The user_id who create the record.
    .. attribute:: update_time
        The datetime of the recode when be updated.
    .. attribute:: update_time
        The user_id who update the record.
    """
    create_time = Column('create_time', DateTime(), default=now(), nullable=False)
    creator = Column('creator', String(50), nullable=False)
    update_time = Column('update_time', DateTime(), default=now(), nullable=False)
    updater = Column('updater', String(50), nullable=False)