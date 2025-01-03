from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, delete, select
from sqlalchemy.orm import selectinload

from models import Ban, Board, Comment, Post, Role, RoleLevel
from schemas.comment import CommentCreate, CommentPublic, CommentUpdate
from schemas.user import UserPublic
from utils import update_fields

import services.core as core_service


async def get_comments_by_query(session: AsyncSession, user_public: UserPublic, where) -> list[CommentPublic]:
    user_id = user_public.id if user_public != None else -1

    query = (
        select(Comment, Role.level, func.count(Ban.id))
        .where(where)
        .join(Post, Post.id == Comment.post_id)
        .join(
            Role,
            (Role.board_id == Post.board_id) & (Role.user_id == user_id),
            isouter=True,
        )
        .join(
            Ban,
            (Ban.board_id == Post.board_id) & (Role.user_id == user_id),
            isouter=True,
        )
        .options(selectinload(Comment.user), selectinload(Comment.post).selectinload(Post.board))
        .group_by(Comment.id, Role.id)
    )

    results = await session.execute(query)

    comments_public = []
    for comment, role_level, ban in results:
        comment: Comment
        role_level: RoleLevel

        access_level = await core_service.get_access_level(
            session,
            Comment,
            model=comment,
            user_public=user_public,
            role_level=RoleLevel.user if not role_level else role_level,
            ban=ban > 0,
        )

        hidden_by_parent = comment.post.hidden or comment.user.hidden or comment.post.board.hidden

        comment_public = CommentPublic(
            **vars(comment), hidden_by_parent=hidden_by_parent, access_level=access_level
        )
        comments_public.append(comment_public)

    return comments_public


async def get_comment_by_query(session: AsyncSession, user_public: UserPublic, where) -> CommentPublic | None:
    comments_public = await get_comments_by_query(session, user_public, where)

    if len(comments_public) == 0:
        return None
    return comments_public[0]
