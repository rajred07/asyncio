from pydantic import BaseModel

class LikeResponse(BaseModel):
    """Response when user likes/unlikes a playlist"""
    liked: bool  # Current state after toggle
    likes_count: int  # Total likes on the playlist

class SaveResponse(BaseModel):
    """Response when user saves/unsaves a playlist"""
    saved: bool       # Current state after toggle
    saves_count: int  # Total saves on the playlist

class UserInteractionsResponse(BaseModel):
    """User's interaction state with a playlist"""
    is_liked: bool
    is_saved: bool