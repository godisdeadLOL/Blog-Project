from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, exists, select, delete
from sqlalchemy.orm import joinedload

from models import Ban, Board, Post, Role, RoleLevel, User

from schemas.board import BoardCreate, BoardPublic, BoardUpdate
from schemas.user import UserPublic
from utils import update_fields

import services.core as core_service


async def get_boards_by_query(session: AsyncSession, user_public: UserPublic, where) -> list[BoardPublic]:
    user_id = user_public.id if user_public != None else -1

    query = (
        select(Board, Role.level, func.count(Post.id), func.count(Ban.id))
        .where(where)
        .join(Role, (Role.board_id == Board.id) & (Role.user_id == user_id), isouter=True)
        .join(Ban, (Ban.board_id == Board.id) & (Role.user_id == user_id), isouter=True)
        .join(Post, Post.board_id == Board.id, isouter=True)
        .group_by(Board.id, Role.id)
    )

    results = await session.execute(query)

    boards_public = []
    for board, role_level, posts_count, ban in results:
        board: Board
        role_level: RoleLevel

        access_level = await core_service.get_access_level(
            session,
            Board,
            model=board,
            user_public=user_public,
            role_level=RoleLevel.user if not role_level else role_level,
            ban=ban > 0,
        )

        board_public = BoardPublic(**vars(board), access_level=access_level, posts_count=posts_count)
        boards_public.append(board_public)

    return boards_public


async def get_board_by_query(session: AsyncSession, user_public: UserPublic, where) -> BoardPublic | None:
    posts = await get_boards_by_query(session, user_public, where)

    if len(posts) == 0:
        return None

    return posts[0]
