from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session

from dependencies import get_current_user, get_current_user_or_none
from exceptions import NoBoardException, NoUserException, WrongAccessException

from models import Ban, Board, Role, RoleLevel, User

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
    if not await core_service.model_exists(session, User, user_id):
        raise NoUserException()

    roles_public = await role_service.get_roles_by_query(session, user_public, Role.user_id == user_id)
    return roles_public


@router.get("/board/{board_id}", response_model=list[RolePublic])
async def get_roles_by_board_id(
    board_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    if not await core_service.model_exists(session, Board, board_id):
        raise NoBoardException()

    roles_public = await role_service.get_roles_by_query(session, user_public, Role.board_id == board_id)
    return roles_public


@router.post("/", response_model=RolePublic)
async def create_role(
    role_create: RoleCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not await core_service.model_exists(session, Board, role_create.board_id):
        raise NoBoardException()

    if not await core_service.model_exists(session, User, role_create.user_id):
        raise NoUserException()

    user_access_level = await core_service.get_access_level(
        session, Board, model_id=role_create.board_id, user_public=user_public
    )

    target_access_level = await core_service.get_access_level(
        session, Board, model_id=role_create.board_id, user_id=role_create.user_id
    )

    if not (
        user_access_level == RoleLevel.owner
        or (
            user_access_level >= RoleLevel.admin.value
            and user_access_level.value > target_access_level.value
            and user_access_level.value > role_create.level.value
        )
    ):
        raise WrongAccessException()

    # удалить баны
    current_ban: Ban | None = await core_service.get_model(
        session, Ban, (Ban.board_id == role_create.board_id) & (Ban.user_id == role_create.user_id)
    )

    if current_ban != None:
        await core_service.delete_model(session, Ban, current_ban.id)

    # удалить текущую роль
    current_role: Role | None = await core_service.get_model(
        session, Role, (Role.board_id == role_create.board_id) & (Role.user_id == role_create.user_id)
    )

    if current_role != None:
        await core_service.delete_model(session, Role, current_role.id)

    # передать owner
    if role_create.level == RoleLevel.owner:
        owner_role: Role | None = await core_service.get_model(
            session, Role, (Role.board_id == role_create.board_id) & (Role.user_id == user_public.id)
        )

        if owner_role != None:
            await core_service.delete_model(session, Role, owner_role.id)

        await core_service.create_model(
            session, Role, user_id=user_public.id, board_id=role_create.board_id, level=RoleLevel.admin
        )

    role = await core_service.create_model(session, Role, role_create)
    role_public = await role_service.get_role_by_query(session, user_public, Role.id == role.id)

    return role_public
