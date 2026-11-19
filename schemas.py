from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field



# ==================== USER ==================== #
class UserBase(BaseModel):
    """Fields shared between input and output schemas."""
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=60)
    bio: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):

    password: str = Field(..., min_length=4, max_length=128)


class UserUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    bio: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=4, max_length=128)


class UserPublic(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    bio: Optional[str] = None
    created_at: datetime


class UserOut(UserPublic):

    user_id: int
    email: EmailStr
    updated_at: datetime


class UserWithCounts(UserOut):

    post_count: int = 0
    followers_count: int = 0
    following_count: int = 0



# ==================== POST ==================== #
class PostBase(BaseModel):

    content: str = Field(..., min_length=1, max_length=500)
    image_url: Optional[str] = Field(None, max_length=255)


class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):

    content: Optional[str] = Field(None, min_length=1, max_length=500)
    image_url: Optional[str] = Field(None, max_length=255)


class PostOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    post_id: int
    content: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    author: UserPublic



# ==================== FOLLOW ==================== #
class FollowOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    follower_id: int
    following_id: int
    created_at: datetime



# ==================== AUTH ==================== #
class Token(BaseModel):

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):

    user_id: Optional[int] = None


class LoginRequest(BaseModel):

    email: EmailStr
    password: str



# ==================== PAGINATION ==================== #
class PaginatedPosts(BaseModel):

    total: int
    items: List[PostOut]