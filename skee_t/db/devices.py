#! -*- coding: utf-8 -*-
from sqlalchemy import Integer, String, BigInteger, Boolean, Text
from sqlalchemy import Column
from skee_t.db.model_base import DB_BASE_MODEL, GenericModel

__author__ = 'pluto'


class NetworkDevice(DB_BASE_MODEL, GenericModel):
    """
    A class which represents generic attributes of network devices.
    Every network device class will be extend from this model.
    .. attribute:: id
        The identity of network device.
    .. attribute:: device_type
        The type of network device. The values include S(Switcher)/R(Router)/L(LoadBalancer)/F(Firewall)
    .. attribute:: name

    .. attribute:: manufacturer

    .. attribute:: backplane_bandwidth

    .. attribute:: throughput

    .. attribute:: port_count

    .. attribute:: management_mode

    .. attribute:: state

    .. attribute:: disabled

    .. attribute:: os_version

    .. attribute:: priority

    """
    id = Column('id', BigInteger(20), autoincrement=True, primary_key=True)
    device_type = Column('device_type', String(4), nullable=True)
    name = Column('name', String(255), nullable=False)
    uuid = Column('uuid', String(100), nullable=False, unique=True)
    manufacturer = Column('manufacturer', String(255))
    backplane_bandwidth = Column('backplane_bandwidth', BigInteger(20))
    throughput = Column('throughput', BigInteger(20))
    port_count = Column('port_count', Integer(4))
    management_mode = Column('management_mode', String(255))
    state = Column('state', String(10), default='ACTIVE')
    disabled = Column('disabled', Boolean, default=False)
    os_version = Column('os_version', String(255))
    priority = Column('priority', Integer(4))


