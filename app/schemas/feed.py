from pydantic import BaseModel
from typing import List, Optional
from schemas.playlist import PlaylistResponse

class FeedFilters(BaseModel):
    """Active filters applied to the feed"""
    category: Optional[str] = None
    scenario: Optional[str] = None
    vibes: Optional[List[str]] = None

class FeedResponse(BaseModel):
    """Paginated feed response with metadata"""
    playlists: List[PlaylistResponse]
    total: int  # Total playlists matching filters
    page: int  # Current page number
    page_size: int  # Items per page
    total_pages: int  # Total number of pages
    has_next: bool  # Is there a next page?
    has_prev: bool  # Is there a previous page?
    sort: str  # Sort method used (popular/recent/trending)
    filters: Optional[FeedFilters] = None  # Active filters