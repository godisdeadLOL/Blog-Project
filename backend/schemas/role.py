from typing import Optional
from pydantic import BaseModel

from models import RoleLevel
from schemas.board import BoardPublic
from schemas.user import UserPublic


class RolePublic(BaseModel):
    id: int

    user: UserPublic
    board: BoardPublic

    level: RoleLevel


class RoleCreate(BaseModel):
    user_id: int
    board_id: int
    level: RoleLevel
