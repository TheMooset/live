import time
from typing import List, Union

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter

from config import config


class User(BaseModel):
    id: int
    name: str
    hash_id: str
    avatar: Union[str, None]

    def __init__(self, **data):
        if data['avatar'] is not None:
            data['avatar'] = data['avatar']['small']

        super().__init__(**data)


class CoreService:
    __connection = None
    default_user_data = {'id': None, 'name': 'کاربر مهمان', 'hash_id': None, 'avatar': None}

    base_url = config.core_url
    headers = {
        'User-Agent': 'live-shopping'
    }

    @classmethod
    def __get_connection(cls):
        if not cls.__connection:
            cls.__connection = cls.__create_session()
        return cls.__connection

    @classmethod
    def __create_session(cls):
        session = requests.session()
        session.mount(cls.base_url, HTTPAdapter(max_retries=3))
        return session

    @classmethod
    def products_by_ids(cls, product_ids: List[int]):
        if len(product_ids) == 0:
            return []
        response = cls.__get_connection().get(cls.base_url + "/api_v2/product/list/", headers=cls.headers,
                                              params={"product_ids": product_ids}, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve vendor with error: {response.text}")

        return response.json()['products']

    @classmethod
    def users_by_ids(cls, user_ids: List[int]):
        if len(user_ids) == 0:
            return []
        response = cls.__get_connection().get(cls.base_url + "/api_v2/user/get-by-ids/", headers=cls.headers,
                                              params={"user_ids": user_ids}, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve vendor with error: {response.text}")

        return response.json()

    @classmethod
    def current_user_data(cls, token: str):
        response = cls.__get_connection().get(cls.base_url + "/api_v2/user",
                                              headers={**cls.headers, "Authorization": token}, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve vendor with error: {response.text}")

        return response.json()

    @classmethod
    def get_users_data(cls, user_ids: List[int]):
        limit = 50
        result = []
        for i in range(int(len(user_ids) / limit) + 1):
            offset = i * limit
            result.extend(cls.users_by_ids(user_ids=user_ids[offset: offset + limit]))
            time.sleep(0.02)

        users = {a['id']: User(**a).dict() for a in result}
        result_user_ids = [a['id'] for a in result]
        for user_id in user_ids:
            if user_id not in result_user_ids:
                users[user_id] = cls.default_user_data

        return users

    @classmethod
    def get_user_data(cls, user_id: Union[int, None]):
        return cls.get_users_data([user_id])[user_id] if user_id is not None else cls.default_user_data
