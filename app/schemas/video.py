from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VideoCreate(BaseModel):
    youtube_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=300)
    channel_name: str = Field(..., min_length=1, max_length=200)
    thumbnail: Optional[str] = None
    views: Optional[int] = 0
    duration: Optional[int] = 0  # Duration in seconds
    youtube_description: Optional[str] = None
    user_description: Optional[str] = None
    position: Optional[int] = 0

class VideoUpdate(BaseModel):
    user_description: Optional[str] = None
    position: Optional[int] = None

class VideoResponse(BaseModel):
    id: int
    youtube_id: str
    title: str
    channel_name: str
    thumbnail: Optional[str]
    views: int
    duration: int  # Duration in seconds
    youtube_description: Optional[str]
    user_description: Optional[str]
    playlist_id: int
    added_by_id: Optional[int]
    position: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True