#! -*-coding: UTF-8 -*-
from setuptools import setup, find_packages

__author__ = 'pluto'

setup(
    name='skee_t',
    version='0.1.0',
    author='Skee_T Technology Team',
    url='http://.skee_t.com',
    description='README.md',
    packages=find_packages(),
    package_dir={'skee_t': 'skee_t'},
    install_requires=[
        'Paste<=1.7.5.1',
        'PasteDeploy<=1.5.2,>=1.5.0',
        'WebOb<=1.3.1,>=1.2.3',
        'Routes!=2.0,<=2.1,>=1.12.3',
        'anyjson<=0.3.3,>=0.3.3',
        'eventlet<=0.15.2,>=0.15.1',
        'greenlet<=0.4.2,>=0.3.2',
        'httplib2<=0.9,>=0.7.5',
        'iso8601<=0.1.10,>=0.1.9',
        'jsonrpclib<=0.1.3',
        'netaddr<=0.7.13,>=0.7.12',
        'SQLAlchemy!=0.9.0,!=0.9.1,!=0.9.2,!=0.9.3,!=0.9.4,!=0.9.5,!=0.9.6,<=0.9.99,>=0.8.4',
        'mysql-connector==2.1.3',
        'oslo.config>=1.4.0',

    ],
    data_files=[
        ('/etc/skee_t', ['etc/skee_t.conf', 'etc/skee_t_logging.conf']),
        ('/etc/skee_t/paste', ['etc/paste/skee_t.ini']),
        ('/var/log/skee_t', []),
    ],
    classifiers=[
        'Development Status :: 3 - alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Bug Tracking',
    ],
    entry_points={
        'console_scripts': [
            'skee_t = skee_t.main:main',
        ],
    },
)

