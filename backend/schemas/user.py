from typing import Optional
from pydantic import BaseModel
from models import RoleLevel


class UserPublic(BaseModel):
    id: int
    hidden: bool = False
    name: str
    superuser_level: RoleLevel


class UserBoard(UserPublic):
    role_level: RoleLevel

class UserUpdate(BaseModel):
    name: Optional[str] = None
    hidden: Optional[bool] = None