from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.base import BaseModelHideable


class CommentPublic(BaseModelHideable):
    id: int
    content: str
    post_id: int
    user_id: int


class CommentCreate(BaseModel):
    content: str
    post_id: int


class CommentUpdate(BaseModel):
    content: Optional[str]
    hidden: Optional[bool]
