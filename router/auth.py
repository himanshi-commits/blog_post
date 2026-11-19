from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import create_access_token, password_hashing, password_verifying
from database import get_db_session
from models import User
from schemas import UserCreate, UserOut, Token
from crud import get_user_by_email, create_user

 
router = APIRouter(prefix="/auth", tags=["auth"])


# =================== SIGNUP (register a new user) ===================
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # Check if email is already taken
    existing = await get_user_by_email(db=db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Hash the password
    payload.password = password_hashing(payload.password)

    # Create the user
    user = await create_user(db, payload)

    # Return the public fields (no password)
    return user


# =================== LOGIN (issue a JWT) ===================
@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    user = await get_user_by_email(db, form.username)
    if user is None or not password_verifying(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({"sub": str(user.user_id)})
    return {"access_token": token, "token_type": "bearer"}
