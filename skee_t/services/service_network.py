#! -*- coding: UTF-8 -*-
import json
from skee_t.services import BaseService
from skee_t.services.service_validator import NetworkCreateValidator

__author__ = 'pluto'


class NetworkService(BaseService):
    """

    """

    def __init__(self):
        pass

    @NetworkCreateValidator
    def create_device(self, dict_args={}):
        location = Location(dc_uuid=dict_args.get('dc_uuid'),
                            cabinet_uuid=dict_args.get('cabinet_uuid'),
                            start_u_index=dict_args.get('start_u_index'),
                            end_u_index=dict_args.get('end_u_index'),
                            creator=dict_args.get('creator'),
                            create_time=dict_args.get('create_time'),
                            updater=dict_args.get('updater'),
                            update_time=dict_args.get('update_time'))

        job_attrs = dict()
        job_attrs['ip'] = dict_args.get('ip')
        job_attrs_json = json.dumps(job_attrs)

        job = Job(job_type=JobType.SCAN,
                  state=JobState.NEW,
                  deleted=False,
                  job_attrs=job_attrs_json)

        session = None
        try:
            engine = DbEngine().get_instance()
            session = engine.get_session(autocommit=False, expire_on_commit=True)
            # Save current location and job information
            session.add(location)
            session.add(job)
            session.commit()
            JobEngine().execute(job)
        except Exception as e:
            if session is not None:
                session.rollback()
            raise e
