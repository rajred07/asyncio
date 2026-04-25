# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from database import get_db
# from crud.user import UserCRUD
# from schemas.user import (
#     UserCreate, UserUpdate, UserResponse, UserLogin, 
#     Token, UserPublicProfile
# )
# from utils.auth import create_access_token, get_current_active_user
# from models.user import User
# from typing import List

# router = APIRouter(prefix="/api/users", tags=["users"])

# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
#     """Register a new user"""
#     # Check if email already exists
#     existing_user = await UserCRUD.get_by_email(db, user_data.email)
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )
    
#     # Check if username already exists
#     existing_username = await UserCRUD.get_by_username(db, user_data.username)
#     if existing_username:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Username already taken"
#         )
    
#     # Create user
#     user = await UserCRUD.create(db, user_data)
#     return user

# @router.post("/login", response_model=Token)
# async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
#     """Login user and return JWT token"""
#     # Get user by email
#     user = await UserCRUD.get_by_email(db, user_credentials.email)
    
#     if not user or not UserCRUD.verify_password(user_credentials.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Create access token
#     access_token = create_access_token(data={"sub": str(user.id)})
    
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/me", response_model=UserResponse)
# async def get_current_user_profile(
#     current_user: User = Depends(get_current_active_user)
# ):
#     """Get current user's profile"""
#     return current_user

# @router.put("/me", response_model=UserResponse)
# async def update_current_user_profile(
#     user_data: UserUpdate,
#     current_user: User = Depends(get_current_active_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update current user's profile"""
#     updated_user = await UserCRUD.update(db, current_user.id, user_data)
#     if not updated_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return updated_user

# @router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_current_user(
#     current_user: User = Depends(get_current_active_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete current user's account"""
#     await UserCRUD.delete(db, current_user.id)
#     return None

# @router.get("/{username}", response_model=UserPublicProfile)
# async def get_user_by_username(
#     username: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get user profile by username (public)"""
#     user = await UserCRUD.get_by_username(db, username)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user

# @router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
# async def follow_user(
#     user_id: int,
#     current_user: User = Depends(get_current_active_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Follow a user"""
#     success = await UserCRUD.follow_user(db, current_user.id, user_id)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot follow this user"
#         )
#     return {"message": "Successfully followed user"}

# @router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
# async def unfollow_user(
#     user_id: int,
#     current_user: User = Depends(get_current_active_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Unfollow a user"""
#     success = await UserCRUD.unfollow_user(db, current_user.id, user_id)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot unfollow this user"
#         )
#     return {"message": "Successfully unfollowed user"}

# @router.get("/{user_id}/followers", response_model=List[UserPublicProfile])
# async def get_user_followers(
#     user_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all followers of a user"""
#     followers = await UserCRUD.get_followers(db, user_id)
#     return followers

# @router.get("/{user_id}/following", response_model=List[UserPublicProfile])
# async def get_user_following(
#     user_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all users that a user follows"""
#     following = await UserCRUD.get_following(db, user_id)
#     return following


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.user import UserCRUD
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    Token, UserPublicProfile
)
from utils.auth import create_access_token, get_current_active_user, oauth2_scheme, SECRET_KEY, ALGORITHM
from models.user import User
from utils.cache import blacklist_token
from jose import jwt as jose_jwt
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = await UserCRUD.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await UserCRUD.get_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = await UserCRUD.create(db, user_data)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT token (OAuth2 compatible)"""
    # Try to find user by email first, then by username
    user = await UserCRUD.get_by_email(db, form_data.username)
    if not user:
        user = await UserCRUD.get_by_username(db, form_data.username)
    
    if not user or not UserCRUD.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user),
):
    """
    Invalidate the current JWT token server-side by adding its jti to the
    Redis blacklist. The client should also delete the token from localStorage.
    """
    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            # TTL = remaining seconds until the token naturally expires
            remaining_ttl = int(exp - datetime.now(timezone.utc).timestamp())
            if remaining_ttl > 0:
                blacklist_token(jti, remaining_ttl)
    except Exception:
        pass  # Token already expired or malformed — nothing to blacklist
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    updated_user = await UserCRUD.update(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user's account"""
    await UserCRUD.delete(db, current_user.id)
    return None

@router.get("/{username}", response_model=UserPublicProfile)
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user profile by username (public)"""
    user = await UserCRUD.get_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow a user"""
    success = await UserCRUD.follow_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow this user"
        )
    return {"message": "Successfully followed user"}

@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user"""
    success = await UserCRUD.unfollow_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unfollow this user"
        )
    return {"message": "Successfully unfollowed user"}

@router.get("/{user_id}/followers", response_model=List[UserPublicProfile])
async def get_user_followers(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all followers of a user"""
    followers = await UserCRUD.get_followers(db, user_id)
    return followers

@router.get("/{user_id}/following", response_model=List[UserPublicProfile])
async def get_user_following(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all users that a user follows"""
    following = await UserCRUD.get_following(db, user_id)
    return following