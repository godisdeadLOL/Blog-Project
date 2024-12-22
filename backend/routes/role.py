from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session

from dependencies import get_current_user, get_current_user_or_none
from exceptions import NoBoardException, NoUserException, WrongAccessException

from models import Board, Role, RoleLevel

from schemas.role import RoleCreate, RolePublic
from schemas.user import UserPublic

import services.board as board_service
import services.user as user_service
import services.role as role_service
import services.core as core_service

router = APIRouter()


@router.get("/user/{user_id}", response_model=list[RolePublic])
async def get_roles_by_user_id(
    user_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    roles_public = await role_service.get_roles_by_query(session, user_public, Role.user_id == user_id)
    return roles_public


@router.get("/board/{board_id}", response_model=list[RolePublic])
async def get_roles_by_board_id(
    board_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    roles_public = await role_service.get_roles_by_query(session, user_public, Role.board_id == board_id)
    return roles_public


@router.post("/", response_model=RolePublic)
async def create_role(
    role_create: RoleCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not await board_service.board_exists(session, role_create.board_id):
        raise NoBoardException()

    if not await user_service.user_exists(session, role_create.user_id):
        raise NoUserException()

    user_access_level = await core_service.get_access_level(
        session, Board, model_id=role_create.board_id, user_public=user_public
    )

    target_access_level = await core_service.get_access_level(
        session, Board, model_id=role_create.board_id, user_id=role_create.user_id
    )

    # да не понимаю

    if not (
        user_access_level == RoleLevel.owner
        or (
            user_access_level >= RoleLevel.admin.value
            and user_access_level.value > target_access_level.value
            and user_access_level.value > role_create.level.value
        )
    ):
        raise WrongAccessException()

    # todo: удалять уже существующую роль на борде

    role = Role(**role_create.model_dump())

    session.add(role)
    await session.commit()
    await session.refresh(role)

    return role
