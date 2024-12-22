from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, delete, select
from sqlalchemy.orm import joinedload

from exceptions import NoUserException
from models import Board, Role, User
from schemas.role import RolePublic
from schemas.user import UserPublic
from utils import update_fields

import services.board as board_service
import services.user as user_service


async def get_roles_by_query(session: AsyncSession, user_public: UserPublic, where):
    query = select(Role).where(where).options(joinedload(Role.user))
    roles = (await session.execute(query)).scalars().all()

    board_ids = set(role.board_id for role in roles)
    boards_public = await board_service.get_boards_by_query(session, user_public, Board.id.in_(board_ids))

    id_to_board_public = {board_public.id: board_public for board_public in boards_public}

    roles_public = []
    for role in roles:
        role_public = RolePublic(
            id=role.id,
            level=role.level,
            user=UserPublic.model_validate(vars(role.user)),
            board=id_to_board_public[role.board_id],
        )
        roles_public.append(role_public)

    return roles_public