from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from datetime import datetime
from enum import Enum


class RoleLevel(int, Enum):
    user = 0
    creator = 1
    moderator = 2
    admin = 3
    owner = 4


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()

    superuser_level: Mapped[RoleLevel] = mapped_column(default=RoleLevel.user)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    roles: Mapped[list["Role"]] = relationship(back_populates="user")
    bans: Mapped[list["Ban"]] = relationship(back_populates="user")


class Board(Base):
    __tablename__ = "Board"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    posts: Mapped[list["Post"]] = relationship(back_populates="board")
    roles: Mapped[list["Role"]] = relationship(back_populates="board")
    bans: Mapped[list["Ban"]] = relationship(back_populates="board")


class Role(Base):
    __tablename__ = "Role"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)

    level: Mapped[RoleLevel] = mapped_column(default=RoleLevel.user)

    user_id: Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="roles")

    board_id: Mapped[int] = mapped_column(ForeignKey("Board.id", ondelete="CASCADE"))
    board: Mapped[Board] = relationship(back_populates="roles")


class Post(Base):
    __tablename__ = "Post"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    user_id: Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="posts")

    board_id: Mapped[int] = mapped_column(ForeignKey("Board.id", ondelete="CASCADE"))
    board: Mapped[Board] = relationship(back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship(back_populates="post")


class Comment(Base):
    __tablename__ = "Comment"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    content: Mapped[str] = mapped_column()

    post_id: Mapped[int] = mapped_column(ForeignKey("Post.id", ondelete="CASCADE"))
    post: Mapped[Post] = relationship(back_populates="comments")

    user_id: Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="comments")


class Ban(Base):
    __tablename__ = "Ban"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="bans")

    board_id: Mapped[int] = mapped_column(ForeignKey("Board.id", ondelete="CASCADE"))
    board: Mapped[Board] = relationship(back_populates="bans")
