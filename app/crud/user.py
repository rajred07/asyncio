# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from models.user import User
# from schemas.user import UserCreate, UserUpdate
# from typing import Optional
# import bcrypt

# class UserCRUD:
#     @staticmethod
#     def hash_password(password: str) -> str:
#         # Convert to bytes and hash with bcrypt
#         pwd_bytes = password.encode('utf-8')
#         salt = bcrypt.gensalt()
#         hashed = bcrypt.hashpw(pwd_bytes, salt)
#         return hashed.decode('utf-8')
    
#     @staticmethod
#     def verify_password(plain_password: str, hashed_password: str) -> bool:
#         # Convert both to bytes and verify
#         pwd_bytes = plain_password.encode('utf-8')
#         hashed_bytes = hashed_password.encode('utf-8')
#         return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    
#     @staticmethod
#     async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
#         """Get user by ID with followers/following loaded"""
#         result = await db.execute(
#             select(User)
#             .options(selectinload(User.followers), selectinload(User.following))
#             .where(User.id == user_id)
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
#         """Get user by email"""
#         result = await db.execute(select(User).where(User.email == email))
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
#         """Get user by username"""
#         result = await db.execute(
#             select(User)
#             .options(selectinload(User.followers), selectinload(User.following))
#             .where(User.username == username)
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def create(db: AsyncSession, user_data: UserCreate) -> User:
#         """Create new user"""
#         hashed_pwd = UserCRUD.hash_password(user_data.password)
        
#         new_user = User(
#             username=user_data.username,
#             email=user_data.email,
#             hashed_password=hashed_pwd,
#             full_name=user_data.full_name
#         )
        
#         db.add(new_user)
#         await db.commit()
#         await db.refresh(new_user)
#         return new_user
    
#     @staticmethod
#     async def update(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
#         """Update user profile"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return None
        
#         update_data = user_data.model_dump(exclude_unset=True)
#         for field, value in update_data.items():
#             setattr(user, field, value)
        
#         await db.commit()
#         await db.refresh(user)
#         return user
    
#     @staticmethod
#     async def delete(db: AsyncSession, user_id: int) -> bool:
#         """Delete user"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return False
        
#         await db.delete(user)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
#         """Follow a user"""
#         if follower_id == following_id:
#             return False
        
#         follower = await UserCRUD.get_by_id(db, follower_id)
#         user_to_follow = await UserCRUD.get_by_id(db, following_id)
        
#         if not follower or not user_to_follow:
#             return False
        
#         if user_to_follow in follower.following:
#             return False
        
#         follower.following.append(user_to_follow)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
#         """Unfollow a user"""
#         follower = await UserCRUD.get_by_id(db, follower_id)
#         user_to_unfollow = await UserCRUD.get_by_id(db, following_id)
        
#         if not follower or not user_to_unfollow:
#             return False
        
#         if user_to_unfollow not in follower.following:
#             return False
        
#         follower.following.remove(user_to_unfollow)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def get_followers(db: AsyncSession, user_id: int):
#         """Get all followers of a user"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return []
#         return user.followers
    
#     @staticmethod
#     async def get_following(db: AsyncSession, user_id: int):
#         """Get all users that a user follows"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return []
#         return user.following

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete, insert
from sqlalchemy.orm import selectinload
from models.user import User, followers_table
from schemas.user import UserCreate, UserUpdate
from typing import Optional, List
import bcrypt

class UserCRUD:
    @staticmethod
    def hash_password(password: str) -> str:
        # Convert to bytes and hash with bcrypt
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Convert both to bytes and verify
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(User)
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user"""
        hashed_pwd = UserCRUD.hash_password(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd,
            full_name=user_data.full_name
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user profile"""
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Delete user"""
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True
    
    @staticmethod
    async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
        """Follow a user directly modifying association table"""
        if follower_id == following_id:
            return False
        
        # Check if already following to prevent duplicate key error
        if await UserCRUD.is_following(db, follower_id, following_id):
            return False
            
        stmt = insert(followers_table).values(
            follower_id=follower_id, 
            following_id=following_id
        )
        try:
            await db.execute(stmt)
            await db.commit()
            return True
        except:
            await db.rollback()
            return False
    
    @staticmethod
    async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
        """Unfollow a user directly modifying association table"""
        stmt = delete(followers_table).where(
            and_(
                followers_table.c.follower_id == follower_id,
                followers_table.c.following_id == following_id
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def is_following(db: AsyncSession, follower_id: int, following_id: int) -> bool:
        """Check if one user follows another"""
        result = await db.execute(
            select(1).where(
                and_(
                    followers_table.c.follower_id == follower_id,
                    followers_table.c.following_id == following_id
                )
            ).limit(1)
        )
        return result.scalar() is not None
    
    @staticmethod
    async def get_followers(db: AsyncSession, user_id: int):
        """Get all followers of a user"""
        from models.user import followers_table
        
        # Query the followers table directly
        result = await db.execute(
            select(User)
            .join(followers_table, followers_table.c.follower_id == User.id)
            .where(followers_table.c.following_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_following(db: AsyncSession, user_id: int):
        """Get all users that a user follows"""
        from models.user import followers_table
        
        # Query the followers table directly
        result = await db.execute(
            select(User)
            .join(followers_table, followers_table.c.following_id == User.id)
            .where(followers_table.c.follower_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def search_users(
        db: AsyncSession,
        query: str,
        limit: int = 5,
    ) -> List[User]:
        """
        Search users with 3-tier ranking priority:
          Priority 2 (highest) → exact username match
          Priority 1           → username starts with query (prefix match)
          Priority 0 (lowest)  → username or full_name contains query anywhere

        Within each tier, results are ordered by followers_count DESC.
        Caps at `limit` results (default 5).
        """
        from sqlalchemy import case
        from typing import List as TypingList

        q_lower = query.lower()
        q_prefix = f"{q_lower}%"
        q_contains = f"%{q_lower}%"

        priority = case(
            (func.lower(User.username) == q_lower, 2),
            (func.lower(User.username).like(q_prefix), 1),
            else_=0,
        )

        stmt = (
            select(User)
            .where(
                (func.lower(User.username).like(q_contains))
                | (func.lower(func.coalesce(User.full_name, "")).like(q_contains))
            )
            .order_by(priority.desc(), User.followers_count.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from models.user import User
# from schemas.user import UserCreate, UserUpdate
# from typing import Optional
# import bcrypt

# class UserCRUD:
#     @staticmethod
#     def hash_password(password: str) -> str:
#         # Convert to bytes and hash with bcrypt
#         pwd_bytes = password.encode('utf-8')
#         salt = bcrypt.gensalt()
#         hashed = bcrypt.hashpw(pwd_bytes, salt)
#         return hashed.decode('utf-8')
    
#     @staticmethod
#     def verify_password(plain_password: str, hashed_password: str) -> bool:
#         # Convert both to bytes and verify
#         pwd_bytes = plain_password.encode('utf-8')
#         hashed_bytes = hashed_password.encode('utf-8')
#         return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    
#     @staticmethod
#     async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
#         """Get user by ID with following loaded"""
#         result = await db.execute(
#             select(User)
#             .options(selectinload(User.following))
#             .where(User.id == user_id)
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
#         """Get user by email"""
#         result = await db.execute(select(User).where(User.email == email))
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
#         """Get user by username"""
#         result = await db.execute(
#             select(User)
#             .options(selectinload(User.following))
#             .where(User.username == username)
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def create(db: AsyncSession, user_data: UserCreate) -> User:
#         """Create new user"""
#         hashed_pwd = UserCRUD.hash_password(user_data.password)
        
#         new_user = User(
#             username=user_data.username,
#             email=user_data.email,
#             hashed_password=hashed_pwd,
#             full_name=user_data.full_name
#         )
        
#         db.add(new_user)
#         await db.commit()
#         await db.refresh(new_user)
#         return new_user
    
#     @staticmethod
#     async def update(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
#         """Update user profile"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return None
        
#         update_data = user_data.model_dump(exclude_unset=True)
#         for field, value in update_data.items():
#             setattr(user, field, value)
        
#         await db.commit()
#         await db.refresh(user)
#         return user
    
#     @staticmethod
#     async def delete(db: AsyncSession, user_id: int) -> bool:
#         """Delete user"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return False
        
#         await db.delete(user)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
#         """Follow a user"""
#         if follower_id == following_id:
#             return False
        
#         follower = await UserCRUD.get_by_id(db, follower_id)
#         user_to_follow = await UserCRUD.get_by_id(db, following_id)
        
#         if not follower or not user_to_follow:
#             return False
        
#         if user_to_follow in follower.following:
#             return False
        
#         follower.following.append(user_to_follow)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
#         """Unfollow a user"""
#         follower = await UserCRUD.get_by_id(db, follower_id)
#         user_to_unfollow = await UserCRUD.get_by_id(db, following_id)
        
#         if not follower or not user_to_unfollow:
#             return False
        
#         if user_to_unfollow not in follower.following:
#             return False
        
#         follower.following.remove(user_to_unfollow)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def get_followers(db: AsyncSession, user_id: int):
#         """Get all followers of a user"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return []
#         return user.followers
    
#     @staticmethod
#     async def get_following(db: AsyncSession, user_id: int):
#         """Get all users that a user follows"""
#         user = await UserCRUD.get_by_id(db, user_id)
#         if not user:
#             return []
#         return user.following