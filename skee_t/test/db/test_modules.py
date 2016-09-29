#! -*- coding: utf-8 -*-
from unittest import TestCase
import unittest
from sqlalchemy import Column, Integer, String
from skee_t.db import DbEngine, MYSQL_DB_URL
from skee_t.db.model_base import DB_BASE_MODEL

__author__ = 'pluto'


class TestDbModel(DB_BASE_MODEL):

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(100))

    __tablename__ = 'test'


class TestDbEngine(TestCase):

    def testConn(self):
        engine = DbEngine(MYSQL_DB_URL % {'db_type': 'mysql',
                                          'driver': 'mysqlconnector',
                                          'username': 'lycosidae',
                                          'password': 'lycosidae',
                                          'host': '192.168.56.101',
                                          'port': 3306,
                                          'database': 'lycosidae'},
                          3600,
                          10,
                          0,
                          30,
                          'UTF-8',
                          True)
        session = engine.get_session(autocommit=False, expire_on_commit=False)
        # test = TestDbModel(id=5, name='test')
        # session.add(test)
        # session.commit()

        # result = engine._engine.execute('select * from test')
        # self.assertIsNotNone(result, 'Result is None.')
        # for row in result:
        #     print row['id']
        #     print row['name']

        datas = session.query(TestDbModel).filter_by(name='test').all()
        self.assertIsNotNone(datas, 'Result is None.')
        for data in datas:
            self.assertIsNotNone(data.id, 'No attribute named \'id\'')
            self.assertIsNotNone(data.name, 'No attribute named \'name\'')

        test = session.query(TestDbModel).filter_by(name='liubing').first()
        self.assertIsNotNone(test, 'Can not query any result')
        self.assertIsNotNone(test.id, 'No attribute named \'id\'')
        self.assertIsNotNone(test.name, 'No attribute named \'name\'')

        test1 = session.query(TestDbModel).filter_by(name='liubing1').first()
        self.assertIsNone(test1)


if __name__ == '__main__':
    unittest.main()
