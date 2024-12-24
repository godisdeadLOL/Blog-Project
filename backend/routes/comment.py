from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from dependencies import get_current_user, get_current_user_or_none
from exceptions import NoCommentException, NoPostException
from models import Comment, Post
from schemas.comment import CommentCreate, CommentPublic
from schemas.user import UserPublic

import services.comment as comment_service
import services.post as post_service
import services.core as core_service

router = APIRouter()


@router.get("/", response_model=list[CommentPublic])
async def get_all_comments(
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    comments = await comment_service.get_comments_by_query(session, user_public, True)
    return comments


@router.get("/post/{post_id}", response_model=list[CommentPublic])
async def get_comments_by_post_id(
    post_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    comments = await comment_service.get_comments_by_query(session, user_public, Comment.post_id == post_id)
    return comments


@router.get("/user/{user_id}", response_model=list[CommentPublic])
async def get_comments_by_user_id(
    user_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    comments = await comment_service.get_comments_by_query(session, user_public, Comment.user_id == user_id)
    return comments


@router.get("/{comment_id}", response_model=CommentPublic)
async def get_comment_by_id(
    comment_id: int,
    user_public: UserPublic = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    print("getting comment data")
    comment_public = await comment_service.get_comment_by_query(
        session, user_public, Comment.id == comment_id
    )

    if not comment_public:
        raise NoCommentException()

    return comment_public


@router.post("/", response_model=CommentPublic)
async def create_comment(
    comment_create: CommentCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_public = await post_service.get_post_by_query(
        session, user_public, Post.id == comment_create.post_id
    )

    if not post_public:
        raise NoPostException()

    comment = await core_service.create_model(session, Comment, comment_create, user_id=user_public.id)

    comment_public = await comment_service.get_comment_by_query(
        session, user_public, Comment.id == comment.id
    )
    return comment_public
