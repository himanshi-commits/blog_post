# models.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# ==================== User ====================

class User(Base):
    __tablename__ = "users"

    # ---------- Columns ----------
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False, index=True
    )

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---------- Timestamps ----------
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),          # set automatically by the DB on insert
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),          # set on insert
        onupdate=func.now(),                # updated automatically on every UPDATE
        nullable=False,
    )

    # ---------- Relationships ----------
    # 1 user  ->  many posts
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Many-to-many self-referential: following / followers
    following: Mapped[List["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.user_id == Follow.follower_id",
        secondaryjoin="User.user_id == Follow.following_id",
        back_populates="followers",
        lazy="selectin",   # avoids N+1 on feed page
    )

    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.user_id == Follow.following_id",
        secondaryjoin="User.user_id == Follow.follower_id",
        back_populates="following",
        lazy="selectin",
    )

    def __repr__(self):
            return f"<User(id={self.user_id}, email='{self.email}')>"

# ==================== Post ====================

class Post(Base):
    __tablename__ = "posts"

    # ---------- Columns ----------
    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ),
        nullable=False,
        index=True
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )

    # ---------- Relationships ----------
    author: Mapped["User"] = relationship(
        "User",
        back_populates='posts'
    )

    def __repr__(self):
        return f"<Post(id={self.post_id}, user_id={self.user_id})>"

# ==================== Follow ====================
class Follow(Base):
    __tablename__ = "followers"

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )

    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),
        Index("ix_follow_following", "following_id")
    )

    def __repr__(self):
            return f"<Follow({self.follower_id} -> {self.following_id})>"




