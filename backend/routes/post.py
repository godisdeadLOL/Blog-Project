from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

from dependencies import get_current_user, get_current_user_or_none
from exceptions import NoBoardException, NoPostException, WrongAccessException
from models import Board, Post, Role, RoleLevel, User
from schemas.post import PostPublic, PostCreate, PostUpdate
from schemas.user import UserPublic

import services.post as post_service
import services.board as board_service

import services.core as core_service

router = APIRouter()


@router.get("/", response_model=list[PostPublic])
async def get_all_posts(
    user_public: UserPublic = Depends(get_current_user_or_none), session: AsyncSession = Depends(get_session)
):
    posts_public = await post_service.get_posts_by_query(session, user_public, True)
    return posts_public


@router.get("/user/{user_id}", response_model=list[PostPublic])
async def get_posts_by_user_id(
    user_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    # todo: check user not exists

    posts_public = await post_service.get_posts_by_query(session, user_public, Post.user_id == user_id)
    return posts_public


@router.get("/board/{board_id}", response_model=list[PostPublic])
async def get_posts_by_board_id(
    board_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    if not board_service.board_exists(session, board_id):
        raise NoBoardException()

    posts_public = await post_service.get_posts_by_query(session, user_public, Post.board_id == board_id)
    return posts_public


@router.get("/{post_id}", response_model=PostPublic)
async def get_post_by_id(
    post_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    post_public = await post_service.get_post_by_query(session, user_public, Post.id == post_id)
    
    # access_level = await core_service.get_access_level(session, Post, model_id=post_id)
    # print(access_level)

    if not post_public:
        raise NoPostException()

    return post_public


@router.post("/", response_model=PostPublic)
async def create_post(
    post_create: PostCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    board_public = await board_service.get_board_by_query(
        session, user_public, Board.id == post_create.board_id
    )

    if not board_public:
        raise NoBoardException()

    if not board_public.access_level.value >= RoleLevel.creator.value:
        raise WrongAccessException()

    post = await post_service.create_post(session, post_create, user_public)

    post_public = await post_service.get_post_by_query(session, user_public, Post.id == post.id)
    return post_public


@router.put("/{post_id}", response_model=PostPublic)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_public = await post_service.get_post_by_query(session, user_public, Post.id == post_id)

    if not post_public:
        raise NoBoardException()

    if not post_public.access_level.value >= RoleLevel.moderator.value:
        raise WrongAccessException()

    await post_service.update_post(session, post_id, post_update)

    post_public = await post_service.get_post_by_query(session, user_public, Post.id == post_id)
    return post_public


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_public = await post_service.get_post_by_query(session, user_public, Post.id == post_id)

    if not post_public:
        raise NoBoardException()

    if not post_public.access_level.value >= RoleLevel.admin.value:
        raise WrongAccessException()

    await post_service.delete_post(session, post_id)

    return None
