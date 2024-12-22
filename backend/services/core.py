from typing import Any, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, exists, select, delete
from sqlalchemy.orm import joinedload

from models import Ban, Board, Comment, Post, Role, RoleLevel, User
from schemas.user import UserPublic

# todo: оптимизировать в один запрос


async def get_access_level(
    session: AsyncSession,
    model_type,
    model: Optional[Any] = None,
    model_id: Optional[int] = None,
    user_id: Optional[int] = None,
    user_public: Optional[UserPublic] = None,
    role_level: Optional[RoleLevel] = None,
    ban: Optional[bool] = None,
):
    # получить пользователя
    if not user_public and user_id != None:
        user_public = (await session.execute(select(User).where(User.id == user_id))).scalar_one()  # 1 sql
        user_id = user_public.id
    elif user_public != None:
        user_id = user_public.id
    else:
        user_id = -1

    # получить объект модели (post, comment, board)
    if not model:
        query = select(model_type).where(model_type.id == model_id)

        if model_type is Comment:
            query = query.options(joinedload(Comment.post))

        model = (await session.execute(query)).scalar_one()  # 2 sql

    # получить board_id
    board_id = None

    if model_type is Board:
        board_id = model.id
    elif model_type is Post:
        board_id = model.board_id
    elif model_type is Comment:
        board_id = model.post.board_id

    # получить role_level
    if role_level == None:
        role = (
            await session.execute(
                select(Role).where((Role.user_id == user_id) & (Role.board_id == board_id))
            )  # 3 sql
        ).scalar_one_or_none()

        if not role:
            role_level = RoleLevel.user
        else:
            role_level = role.level

    # получить баны
    if ban == None:
        ban = (
            await session.execute(
                select(Ban).where((Ban.user_id == user_id) & (Ban.board_id == board_id))
            )  # 4 sql
        ).scalar_one_or_none() != None

    # найти access_level
    access_level = role_level

    if user_public != None:
        if ban or user_public.hidden:
            access_level = RoleLevel.user
        elif user_public.superuser_level.value > access_level.value:
            access_level = user_public.superuser_level
        elif not model_type is Board and model.user_id == user_id:
            access_level = RoleLevel.owner

    return access_level
