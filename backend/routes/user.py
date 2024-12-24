from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database import get_session

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from exceptions import NoBoardException, WrongAccessException
from models import Role, User
from schemas.user import UserBoard, UserPublic, UserUpdate

import services.board as board_service

router = APIRouter()


# @router.get("/board", response_model=list[UserBoard])
# async def get_users_by_board_id(board_id: int, session: AsyncSession = Depends(get_session)):
    
#     if not await board_service.board_exists(session, board_id) :
#         raise NoBoardException()
    
#     query = select(Role).where(Role.board_id == board_id).options(joinedload(Role.user))
#     roles = (await session.execute(query)).unique().scalars()

#     users_board = [UserBoard(**vars(role.user), role_level=role.level) for role in roles]
#     return users_board


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if user_public.id != user_id:
        raise WrongAccessException()
    
    if user_update.hidden != None :
        raise WrongAccessException()
    
    
    
    return None
