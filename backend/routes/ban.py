from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session

from dependencies import get_current_user
from exceptions import NoBoardException, NoUserException, WrongAccessException
from models import Ban, Board, RoleLevel, User

from schemas.ban import BanCreate, BanPublic
from schemas.user import UserPublic

import services.board as board_service
import services.user as user_service

router = APIRouter()


@router.post("/", response_model=BanPublic)
async def create_ban(
    ban_create: BanCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    board_public = await board_service.get_board_by_query(
        session, user_public, Board.id == ban_create.board_id
    )

    if not board_public:
        raise NoBoardException()

    target_user_public = await user_service.get_user_by_query(session, User.id == ban_create.user_id)

    if not target_user_public:
        raise NoUserException()

    target_board_public = await board_service.get_board_by_query(
        session, target_user_public, Board.id == ban_create.board_id
    )

    assert target_board_public != None

    if not (
        board_public.access_level >= RoleLevel.moderator
        and board_public.access_level.value > target_board_public.access_level.value
    ):
        raise WrongAccessException()

    ban = Ban(**ban_create.model_dump())

    session.add(ban)
    await session.commit()
    await session.refresh(ban)

    return ban
