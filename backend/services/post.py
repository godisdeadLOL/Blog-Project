from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, delete, select
from sqlalchemy.orm import selectinload

from models import Ban, Board, Comment, Post, Role, RoleLevel, User
from schemas.post import PostCreate, PostPublic, PostUpdate
from schemas.user import UserPublic
from utils import update_fields

import services.core as core_service


async def get_posts_by_query(session: AsyncSession, user_public: UserPublic, where) -> list[PostPublic]:
    user_id = user_public.id if user_public != None else -1

    query = (
        select(Post, Role.level, func.count(Comment.id), func.count(Ban.id))
        .where(where)
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
        .join(Comment, Comment.post_id == Post.id, isouter=True)
        .options(selectinload(Post.user), selectinload(Post.board))
        .group_by(Post.id, Role.id)
    )

    results = await session.execute(query)

    posts_public = []
    for post, role_level, comments_count, ban in results.unique():
        post: Post
        role_level: RoleLevel

        access_level = await core_service.get_access_level(
            session,
            Post,
            model=post,
            user_public=user_public,
            role_level=RoleLevel.user if not role_level else role_level,
            ban=ban > 0,
        )

        hidden_by_parent = post.user.hidden or post.board.hidden

        post_public = PostPublic(
            **vars(post),
            hidden_by_parent=hidden_by_parent,
            access_level=access_level,
            comments_count=comments_count
        )
        posts_public.append(post_public)

    return posts_public


async def get_post_by_query(session: AsyncSession, user_public: UserPublic, where) -> PostPublic | None:
    posts_public = await get_posts_by_query(session, user_public, where)

    if len(posts_public) == 0:
        return None
    return posts_public[0]