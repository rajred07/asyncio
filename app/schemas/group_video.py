from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GroupVideoCreate(BaseModel):
    youtube_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=300)
    channel_name: str = Field(..., min_length=1, max_length=200)
    thumbnail: Optional[str] = None
    views: int = 0
    youtube_description: Optional[str] = None
    user_description: Optional[str] = None
    position: int = 0

class GroupVideoUpdate(BaseModel):
    user_description: Optional[str] = None
    position: Optional[int] = None

class GroupVideoResponse(BaseModel):
    id: int
    group_playlist_id: int
    youtube_id: str
    title: str
    channel_name: str
    thumbnail: Optional[str]
    views: int
    youtube_description: Optional[str]
    user_description: Optional[str]
    added_by_id: Optional[int]
    position: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Added by user details
    added_by_username: Optional[str] = None
    
    class Config:
        from_attributes = True