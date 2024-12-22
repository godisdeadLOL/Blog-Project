from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from exceptions import UserBlockedException
from models import User
from schemas.user import UserPublic
from security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# todo: get User instead of UserPublic?


def get_current_user_or_none(token: Annotated[str, Depends(oauth2_scheme)]) -> UserPublic | None:
    if not token:
        return None

    try:
        payload = decode_access_token(token)
    except:
        return None

    return UserPublic(**payload)


def get_current_user(user: UserPublic = Depends(get_current_user_or_none)):
    if not user:
        raise HTTPException(401)
    
    if user.hidden :
        raise UserBlockedException()

    return user
