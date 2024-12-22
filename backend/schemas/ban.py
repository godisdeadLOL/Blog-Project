from pydantic import BaseModel


class BanPublic(BaseModel) :
    id: int
    user_id: int
    board_id: int
    
class BanCreate(BaseModel) :
    user_id: int
    board_id: int