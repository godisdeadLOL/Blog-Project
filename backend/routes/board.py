from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from database import get_session
from dependencies import get_current_user, get_current_user_or_none
from exceptions import WrongAccessException, NoBoardException
from models import Board, Role, RoleLevel
from schemas.board import BoardCreate, BoardPublic, BoardUpdate
from schemas.user import UserPublic

from sqlalchemy.ext.asyncio import AsyncSession

import services.board as board_service

router = APIRouter()


@router.get("/", response_model=list[BoardPublic])
async def get_all_boards(
    user_public: UserPublic = Depends(dependency=get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    boards_public = await board_service.get_boards_by_query(session, user_public, True)
    return boards_public


@router.post("/", response_model=BoardPublic)
async def create_board(
    board_create: BoardCreate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    board = await board_service.create_board(session, board_create, user_public.id)

    board_public = await board_service.get_board_by_query(session, user_public, Board.id == board.id)
    return board_public


@router.put("/{board_id}", response_model=BoardPublic)
async def update_board(
    board_id: int,
    board_update: BoardUpdate,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    board_public = await board_service.get_board_by_query(session, user_public, Board.id == board_id)

    if not board_public:
        raise NoBoardException()

    if board_public.access_level != RoleLevel.owner:
        raise WrongAccessException()

    await board_service.update_board(session, board_id, board_update)

    board_public = await board_service.get_board_by_query(session, user_public, Board.id == board_id)
    return board_public

@router.delete("/{board_id}")
async def delete_board(
    board_id: int,
    user_public: UserPublic = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    board_public = await board_service.get_board_by_query(session, user_public, Board.id == board_id)

    if not board_public:
        raise NoBoardException()

    if board_public.access_level != RoleLevel.owner:
        raise WrongAccessException()

    await board_service.delete_board(session, board_id)

    return None
