from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from database import get_session
from models import User
from schemas.auth import RegisterForm
from schemas.user import UserPublic
from security import create_access_token, get_password_hash, verify_password

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


router = APIRouter()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    username = form_data.username
    password = form_data.password

    query = select(User).where(User.name == username)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(401)

    if not verify_password(password, user.password_hash):
        raise HTTPException(401)

    user_public = UserPublic.model_validate(user, from_attributes=True)
    token = create_access_token(user_public.model_dump())

    return {"access_token": token, "token_type": "bearer"}


# @router.post("/logout")
# async def logout(user = Depends(get_current_user_or_none)):
#     # payload = decode_access_token(token)
#     # return payload
#     return user


@router.post("/temp_register", response_model=UserPublic)
async def register(register_form: RegisterForm, session: AsyncSession = Depends(get_session)):
    password_hash = get_password_hash(register_form.password)

    user = User(name=register_form.username, password_hash=password_hash)

    session.add(user)
    await session.commit()

    return user
