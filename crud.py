from typing import Optional, Sequence

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Post, Follow
from schemas import UserCreate, UserUpdate, PostCreate, PostUpdate



# =============== USER ===============
async def get_user_by_id(db: AsyncSession, user_id: int):

    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):

    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User : 

    user = User(
        name = data.name,
        email = data.email,
        password = data.password,
        bio = data.bio
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User,
                      data: UserUpdate, password: Optional[str] = None):

    if data.name is not None:
        user.name = data.name
    if data.bio is not None:
        user.bio = data.bio
    if password is not None:
        user.password = password

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User):

    await db.delete(user)
    await db.commit()


async def get_user_with_counts(db: AsyncSession, user_id: int):

    user = await db.get(User, user_id)
    if not user:
        return None

    post_count = await db.scalar(
        select(func.count(Post.post_id))
        .where(Post.user_id == user_id)
    )
    followers_count = await db.scalar(
        select(func.count())
        .select_from(Follow)
        .where(Follow.following_id == user_id)
    )
    following_count = await db.scalar(
        select(func.count())
        .select_from(Follow)
        .where(Follow.follower_id == user_id)
    )
    return {
        "user": user,
        "posts_count": post_count or 0,
        "followers_count": followers_count or 0,
        "following_count": following_count or 0
    }



# =============== POST ===============
async def create_post(db: AsyncSession, author_id: int, data: PostCreate):

    post = Post(
        user_id=author_id,
        content=data.content,
        image_url=data.image_url
    )
    db.add(post)
    await db.commit()

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.post_id == post.post_id)
    )
    return result.scalar_one()


async def get_post(db: AsyncSession, post_id: int):

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.post_id == post_id)
    )
    return result.scalar_one_or_none()


async def list_posts_by_user(db: AsyncSession, user_id: int,
                             limit: int = 20, offset: int = 0):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

async def update_post(db: AsyncSession, post: Post, data: PostUpdate):

    if data.content is not None:
        post.content = data.content
    if data.image_url is not None:
        post.image_url = data.image_url

    await db.commit()

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.post_id == post.post_id)
    )
    return result.scalar_one()


async def delete_post(db: AsyncSession, post_id: int):
    post = await get_post(db, post_id)
    if post is None:
        return False
    await db.delete(post)
    await db.commit()
    return True



# =============== FEED ===============
async def get_feed(db: AsyncSession, user_id: int,
                   limit: int = 20, offset: int = 0):
    following_subq = select(Follow.following_id).where(Follow.follower_id == user_id)
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where((Post.user_id == user_id) | (Post.user_id.in_(following_subq)))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()



# =============== FOLLOW ===============
async def follow_user(db: AsyncSession, follower_id: int, target_user_id: int):

    if follower_id == target_user_id:
        return False
    existing = await db.get(Follow, (follower_id, target_user_id))
    if existing:
        return False

    db.add(Follow(follower_id=follower_id, following_id=target_user_id))
    await db.commit()
    return True


async def unfollow_user(db: AsyncSession, follower_id: int, target_user_id: int):

    result = await db.execute(
        delete(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == target_user_id
        )
    )
    await db.commit()
    return result.rowcount > 0


async def list_followers(db: AsyncSession, user_id: int):

    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.user_id)
        .where(Follow.following_id == user_id)
    )
    return result.scalars().all()


async def list_following(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.user_id)
        .where(Follow.follower_id == user_id)
    )
    return result.scalars().all()


