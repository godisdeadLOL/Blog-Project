from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session

from dependencies import get_current_user
from exceptions import NoBoardException, NoUserException, WrongAccessException
from models import Ban, Board, RoleLevel, User

from schemas.ban import BanCreate, BanPublic
from schemas.user import UserPublic

import services.board as board_service
import services.user as user_service
import services.core as core_service

router = APIRouter()


@router.post("/", response_model=BanPublic)
async def create_ban(
    ban_create: BanCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not await core_service.model_exists(session, Board, ban_create.board_id):
        raise NoBoardException()

    if not await core_service.model_exists(session, User, ban_create.user_id):
        raise NoUserException()

    user_access_level = await core_service.get_access_level(
        session, Board, model_id=ban_create.board_id, user_public=user_public
    )

    target_access_level = await core_service.get_access_level(
        session, Board, model_id=ban_create.board_id, user_id=ban_create.user_id
    )

    if not (target_access_level > user_access_level and user_access_level >= RoleLevel.moderator):
        raise WrongAccessException()

    ban = await core_service.create_model(session, Ban, ban_create)

    return ban
