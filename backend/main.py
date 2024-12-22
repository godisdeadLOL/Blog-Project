import asyncio
from fastapi import FastAPI

from routes.board import router as board_router
from routes.role import router as role_router
from routes.post import router as post_router
from routes.comment import router as comment_router
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.ban import router as ban_router

from database import init_db

app = FastAPI(title="Blog API")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(post_router, prefix="/post", tags=["Post"])
app.include_router(comment_router, prefix="/comment", tags=["Comment"])
app.include_router(board_router, prefix="/board", tags=["Board"])
app.include_router(role_router, prefix="/role", tags=["Role"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(ban_router, prefix="/ban", tags=["Ban"])

@app.on_event("startup")
async def on_startup():
    await init_db()
