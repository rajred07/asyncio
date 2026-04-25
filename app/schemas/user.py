from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List

# Base schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_image: Optional[str] = None

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_image: Optional[str] = None
    preferred_categories: Optional[List[str]] = None  # e.g. ["Gaming"] or ["Entertainment"] or both

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str]
    preferred_categories: Optional[List[str]] = None
    followers_count: int
    following_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserPublicProfile(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str]
    followers_count: int
    following_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None