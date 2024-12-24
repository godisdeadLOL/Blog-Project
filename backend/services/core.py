from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, exists, select, delete
from sqlalchemy.orm import joinedload

from routes import role
from utils import update_fields
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

    # получить информацию о модели
    if not model:
        query = select(model_type, Role.level, func.count(Ban.id)).where(model_type.id == model_id)

        if model_type is Comment:
            query = query.join(Post, Comment.post_id == Post.id)

        board_id = Post.board_id
        if model_type is Board:
            board_id = Board.id

        query = (
            query.join(Role, (Role.user_id == user_id) & (Role.board_id == board_id), isouter=True)
            .join(Ban, (Ban.user_id == user_id) & (Ban.board_id == board_id), isouter=True)
            .group_by(model_type.id, Role.id)
        )

        results = (await session.execute(query)).one()

        model = results[0]
        role_level = results[1]
        ban = results[2] > 0
        
    if role_level == None :
        role_level = RoleLevel.user

    assert role_level != None
    assert model != None
    assert ban != None

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


# # получить объект модели (post, comment, board)
# if not model:
#     query = select(model_type).where(model_type.id == model_id)

#     if model_type is Comment:
#         query = query.options(joinedload(Comment.post))

#     model = (await session.execute(query)).scalar_one()  # 2 sql

# # получить board_id
# board_id = None

# if model_type is Board:
#     board_id = model.id
# elif model_type is Post:
#     board_id = model.board_id
# elif model_type is Comment:
#     board_id = model.post.board_id

# # получить role_level
# if role_level == None:
#     role = (
#         await session.execute(
#             select(Role).where((Role.user_id == user_id) & (Role.board_id == board_id))
#         )  # 3 sql
#     ).scalar_one_or_none()

#     if not role:
#         role_level = RoleLevel.user
#     else:
#         role_level = role.level

# # получить баны
# if ban == None:
#     ban = (
#         await session.execute(
#             select(Ban).where((Ban.user_id == user_id) & (Ban.board_id == board_id))
#         )  # 4 sql
#     ).scalar_one_or_none() != None

async def model_exists(session: AsyncSession, model_type, model_id: int):
    query = select(exists().where(model_type.id == model_id))
    result = (await session.execute(query)).scalar_one_or_none()

    return result == True


async def get_model(session: AsyncSession, model_type, where):
    query = select(model_type).where(where)
    model = (await session.execute(query)).scalar_one_or_none()

    return model


async def create_model(session: AsyncSession, model_type, model_create=None, **kwargs):
    values = {} if not model_create else model_create.model_dump()
    model = model_type(**values, **kwargs)

    session.add(model)
    await session.commit()
    await session.refresh(model)

    return model


async def update_model(session: AsyncSession, model_type, model_id: int, model_update=None, **kwargs):
    query = select(model_type).where(model_type.id == model_id)
    model = (await session.execute(query)).scalar_one()

    values = {} if not model_update else model_update.model_dump()
    update_fields(model, {**values, **kwargs})

    await session.commit()
    await session.refresh(model)

    return model


async def delete_model(session: AsyncSession, model_type, model_id: int):
    query = delete(model_type).where(model_type.id == model_id)
    await session.execute(query)
    await session.commit()
