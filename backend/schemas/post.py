from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from models import RoleLevel
from schemas.base import BaseModelHideable


class PostPublic(BaseModelHideable):
    id: int
    
    title: Optional[str] = None
    content: Optional[str] = None
    
    comments_count : Optional[int] = None
    
    user_id: Optional[int] = None
    board_id: Optional[int] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PostCreate(BaseModel):
    title: str
    content: str
    board_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    hidden: Optional[bool] = None
