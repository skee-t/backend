#! -*- coding: UTF-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound

from skee_t.db import DbEngine
from skee_t.db.models import WxAccessToken, WxJSAPIToken
from skee_t.services import BaseService

__author__ = 'rensikun'


LOG = logging.getLogger(__name__)


class wxJsapiTokenService(BaseService):
    """

    """

    def __init__(self):
        pass

    def add(self, uuid, jsapi_token, expires_in):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        wxJSAPIToken = WxJSAPIToken(
            uuid=uuid,
            ticket=jsapi_token,
            expires_in=expires_in
                    )

        session = None
        rst_code = 0
        rst_desc = 'success'
        try:
            session = DbEngine.get_session_simple()
            session.add(wxJSAPIToken)
            session.commit()
        except Exception as e:
            LOG.exception("Create user information error.")
            rst_code = '999999'
            rst_desc = e.message
            if session is not None:
                session.rollback()
        finally:
            session.close()
        return {'rst_code':rst_code, 'rst_desc':rst_desc}

    def query(self, state):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            return session.query(WxJSAPIToken) \
                .filter(WxJSAPIToken.state == state).first()
        except NoResultFound as e:
            LOG.exception("access token error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List WxJSAPIToken error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        finally:
            session.close()
        return {'rst_code': rst_code, 'rst_desc': rst_desc}

    def update(self, uuid, state):
        """
        创建用户方法
        :param dict_args:Map类型的参数，封装了由前端传来的用户信息
        :return:
        """
        session = None
        rst_code = 0
        rst_desc = 'success'

        try:
            session = DbEngine.get_session_simple()
            session.query(WxJSAPIToken)\
                .filter(WxJSAPIToken.uuid == uuid)\
                .update({WxJSAPIToken.state:state}
                           ,synchronize_session=False
                           )
            session.commit()
        except NoResultFound as e:
            LOG.exception("get_user_auth_info error.")
            return None
        except (TypeError, Exception) as e:
            LOG.exception("List SkiResort information error.")
            # 数据库异常
            rst_code = '999999'
            rst_desc = e.message
        finally:
            session.close()
        return {'rst_code': rst_code, 'rst_desc': rst_desc}