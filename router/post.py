from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import get_current_user
from database import get_db_session
from models import Post, User
from schemas import PostCreate, PostOut, PostUpdate
from crud import (
    get_user_by_id,
    create_post as create_post_in_db,
    list_posts_by_user as list_posts_by_user_in_db,
    get_post as get_post_from_db,
    update_post as update_post_in_db,
    delete_post as delete_post_in_db,
)

router = APIRouter(prefix="/post", tags=["post"])

# Create Post
@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):  
    post = await create_post_in_db(db, current_user.user_id, payload)

    return post
    
    

# List My Post (paginated)
@router.get("/me", response_model=List[PostOut])
async def list_my_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):

    result = await list_posts_by_user_in_db(db, current_user.user_id, limit, offset)

    return result



# List Posts by User
@router.get("/user/{user_id}", response_model=List[PostOut])
async def list_posts_by_user(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await list_posts_by_user_in_db(db, user_id, limit, offset)
    return result



# Get one Post
@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db_session)):

    post = await get_post_from_db(db, post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Update my Post
@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    post = await get_post_from_db(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your post")

    post = await update_post_in_db(db, post, payload)

    return post

# Delete my Post
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    post = await get_post_from_db(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your post")

    await delete_post_in_db(db, post_id)
    return None

