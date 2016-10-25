#! -*- coding: UTF-8 -*-
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Text, DateTime, Float, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.sql.functions import now

from skee_t.conf import CONF
from skee_t.db import DbEngine
from skee_t.db.model_base import DB_BASE_MODEL, GenericModel

__author__ = 'pluto'


class SkiResort(DB_BASE_MODEL, GenericModel):
    """
    雪场信息类
    定义雪场信息
    """
    __tablename__ = 'ski_resort'

    id = Column('id', BigInteger, primary_key=True, autoincrement=True)
    name = Column('name', String(255), nullable=False, doc='雪场名称')
    city = Column('city', String(100), nullable=False, doc='雪场所在城市')
    address = Column('address', String(255), nullable=False, doc='雪场具体位置')
    spec_pic = Column('spec_pic', String(255), nullable=False, doc='雪场特色照片')
    trail_pic = Column('trail_pic', String(255), nullable=False, doc='雪场雪道图')
    has_bus = Column('has_bus', Boolean, nullable=False, default=0, doc='是否有班车 0：没有；1：有')
    contact = Column('contact', String(100), nullable=True, doc='雪场联系方式')
    disabled = Column('disabled', Boolean, nullable=False, default=0, doc='用于锁定雪场')
    deleted = Column('deleted', Boolean, nullable=False, default=0, doc='用户逻辑删除')


class User(DB_BASE_MODEL):
    """
    用户信息类
    定义用户基本信息
    .. attribute :: sex
        性别。0：女；1：男。因为男的有棍，女的有洞。
    .. attribute :: age
        这里指的是雪龄，而非年龄
    .. attribute :: appliance
        器具，擅长的滑雪器械
    .. attribute :: disabled
        此字段可用于锁定用户账户
    .. attribute :: deleted
        将用户信息逻辑删除
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    uuid = Column('uuid', String(36), nullable=False, unique=True)
    name = Column('name', String(50), nullable=False)
    real_name = Column('real_name', String(50), nullable=True)
    image_path = Column('image_path', String(255), nullable=False, default='')
    sex = Column('sex', Integer, nullable=False, default=1)
    age = Column('age', Integer, nullable=False, default=0)
    level = Column('level', Integer, nullable=False, default=1)
    contact = Column('contact', String(100), nullable=True)
    appliance = Column('appliance', String(50), nullable=False, default=CONF.default.user_appliance)
    history = Column('history', Text, nullable=False, default=CONF.default.user_image_path)
    create_time = Column('create_time', DateTime, nullable=False, default=now())
    update_time = Column('update_time', DateTime, nullable=False, default=now())
    disabled = Column('disabled', Boolean, nullable=False, default=0)
    deleted = Column('deleted', Boolean, nullable=False, default=0)


class Lesson(DB_BASE_MODEL, GenericModel):
    """
    课程信息类

    .. attribute:: state
        课程状态。取值包括-1：终止；0：可报名；1：满额；2：已开始；3：已结束
    .. attribute:: creator
        创建人，创建此课程的教练ID
    .. attribute:: updater
        修改人，如果是系统自动修改，这修改人可设置为system的默认ID，此ID需要创建库的时候直接生成，作为默认数据。
    .. attribute:: hotspot
        热点，记录关注人数
    .. attribute :: estimate
        课程评价。计算自各个参与者评价的平均值，与星级对应。
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    uuid = Column('uuid', String(36), nullable=False, unique=True)
    title = Column('title', String(255), nullable=False)
    pack_uuid = Column('pack', String(36), nullable=False)
    contact = Column('contact', String(100), nullable=True)
    level_limit = Column('level_limit', Integer, nullable=False, default=1)
    venue = Column('venue', String(255), nullable=False)
    meeting_time = Column('meeting_time', DateTime, nullable=False, default=now())
    quota = Column('quota', Integer, nullable=False, default=1)
    fee = Column('fee', Float(11, 2), nullable=False, default=0.00)
    period = Column('period', Integer, nullable=False, default=0)
    description = Column('description', Text, nullable=True)
    state = Column('state', SmallInteger, nullable=False, default=0)
    deleted = Column('deleted', Boolean, nullable=False, default=0)
    hotspot = Column('hotspot', Integer, nullable=False, default=0)
    estimate = Column('estimate', SmallInteger, nullable=False, default=0)



class LessonMember(DB_BASE_MODEL, GenericModel):
    """
    课程成员类
    .. attribute :: state
        成员状态，显示是否成员正常参与教学活动。取值包括：-1：报名后已退出；0：已报名；1：已完成；
    .. attribute :: estimate
        参与评价，只有为完成状态的成员才能参与评价。整数，数值可与星级对应。
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    lesson_uuid = Column('lesson_uuid', String(36), nullable=False, unique=True)
    user_uuid = Column('user_uuid', String(36), nullable=False, unique=True)
    estimate = Column('estimate', SmallInteger, nullable=False, default=0)
    state = Column('state', SmallInteger, nullable=False, default=1)


class Car(DB_BASE_MODEL, GenericModel):
    """
    班车信息类
    对应班车信息表（Cars）
    .. attribute :: running_no
        车次号。同一班车可也有多个车次。
    .. attribute :: licence
        车牌号
    .. attribute :: state
        班车状态。-1：取消；0：可报名；1：满额；2：已结束
    .. attribute :: type
        班车类型。0：单程；1：往返
    .. attribute :: location
        乘车地点。必填项，不能为空，需要前端业务校验
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    running_no = Column('running_no', String(36), nullable=False, unique=True)
    licence = Column('licence', String(10), nullable=False, unique=True)
    fee = Column('fee', Float(11, 2), nullable=False, default=0.00)
    time = Column('time', DateTime, nullable=False, default=now())
    quota = Column('quota', Integer, nullable=False, default=0)
    interest = Column('interest', Integer, nullable=False, default=0)
    state = Column('state', SmallInteger, nullable=False, default=0)
    type = Column('type', SmallInteger, nullable=False, default=1)
    description = Column('description', Text, nullable=True)
    location = Column('location', String(255), nullable=False)


class CarMember(DB_BASE_MODEL, GenericModel):
    """
    班车成员类
    .. attribute :: running_no
        车次号
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    running_no = Column('running_no', String(36), nullable=False, unique=True)
    user_uuid = Column('user_uuid', String(36), nullable=False, unique=True)
    state = Column('state', SmallInteger, nullable=False, default=1)


class Feedback(DB_BASE_MODEL, GenericModel):
    """
    用户反馈信息表
    .. attribute :: contact
        联系方式，必填项，需要业务校验
    """
    id = Column('id', BigInteger, autoincrement=True, primary_key=True)
    user_uuid = Column('user_uuid', String(36), nullable=False, unique=True)
    contact = Column('contact', String(20), nullable=False)
    content = Column('content', Text, nullable=True)


class System(DB_BASE_MODEL):
    """
    系统表
    定义系统参数
    .. attribute :: params
        系统参数集合，Json字符串的形式直接存储。可包含：客服电话，客服邮箱等系统信息。
    """
    id = Column('id', Integer, autoincrement=True, primary_key=True)
    params = Column('params', Text, nullable=True)

    __tablename__ = 'system'


# 根据class创建表
engine = create_engine(DbEngine.get_instance().get_db_url(), echo=True)
DB_BASE_MODEL.metadata.create_all(engine)
