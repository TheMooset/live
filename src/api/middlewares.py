import json
from fastapi import status
from typing import Optional
from base64 import b64decode
from fastapi import Header, HTTPException


def __get_user_id_from_token(authorization: str):
    if authorization is not None and authorization != '':
        tokens = authorization.split('.')
        if len(tokens) == 3:
            payload = json.loads(b64decode(tokens[1] + '==').decode())
            if 'sub' in payload and payload['sub'].isdigit():
                return int(payload['sub'])
    return None


def get_user_if_from_token_if_exist(authorization: Optional[str] = Header(None)):
    return __get_user_id_from_token(authorization)


def get_user_id_from_token(authorization: str = Header(...)):
    user_id = __get_user_id_from_token(authorization)

    if user_id is not None:
        return user_id

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid authorization header")


async def get_admin_token(admin_token: str = Header(...)):
    if admin_token != "J%CqX^303fCP6hP@IlS&qJ^fD1fFbH!U$DOR$O8bOP#WZm0TYqjJqo":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid admin-token header")
