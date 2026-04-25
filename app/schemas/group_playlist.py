# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional, List

# class GroupPlaylistCreate(BaseModel):
#     title: str = Field(..., min_length=1, max_length=200)
#     description: Optional[str] = None
#     thumbnail: Optional[str] = None

# class GroupPlaylistUpdate(BaseModel):
#     title: Optional[str] = Field(None, min_length=1, max_length=200)
#     description: Optional[str] = None
#     thumbnail: Optional[str] = None

# class GroupPlaylistBase(BaseModel):
#     id: int
#     title: str
#     description: Optional[str]
#     thumbnail: Optional[str]
#     owner_id: int
#     created_at: datetime
#     updated_at: Optional[datetime]
    
#     class Config:
#         from_attributes = True

# class GroupPlaylistResponse(GroupPlaylistBase):
#     video_count: int
#     member_count: int

# class GroupPlaylistDetailResponse(GroupPlaylistBase):
#     video_count: int
#     member_count: int
#     # Will be populated with members and videos when needed


from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class GroupPlaylistCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail: Optional[str] = None

class GroupPlaylistUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail: Optional[str] = None

class GroupPlaylistBase(BaseModel):
    id: int
    title: str
    description: Optional[str]
    thumbnail: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class GroupPlaylistResponse(GroupPlaylistBase):
    video_count: int
    member_count: int

class GroupPlaylistDetailResponse(GroupPlaylistBase):
    video_count: int
    member_count: int
    # Will be populated with members and videos when needed

class PlaylistImportRequest(BaseModel):
    youtube_playlist_url: str = Field(..., min_length=1)
    max_videos: Optional[int] = Field(50, ge=1, le=100)

class PlaylistImportResponse(BaseModel):
    message: str
    task_id: str
    estimated_videos: int
    status_endpoint: str

class ImportStatusResponse(BaseModel):
    task_id: str
    status: str  # "processing" | "completed" | "failed"
    total_videos: int
    imported: int
    failed: int
    skipped_duplicates: int
    progress_percentage: int
    current_video: Optional[str]
    error: Optional[str]