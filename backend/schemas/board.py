from typing import Optional
from pydantic import BaseModel

from schemas.base import BaseModelHideable


class BoardPublic(BaseModelHideable):
    id: int
    name: str
    posts_count: int


class BoardCreate(BaseModel):
    name: str

class BoardUpdate(BaseModel):
    name: Optional[str] = None