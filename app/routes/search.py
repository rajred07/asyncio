from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from utils.auth import get_current_active_user
from models.user import User
from crud.playlist import PlaylistCRUD
from crud.user import UserCRUD
from schemas.playlist import PlaylistResponse
from schemas.user import UserResponse
from pydantic import BaseModel
from typing import List, Optional, Literal

router = APIRouter(prefix="/api/search", tags=["Search"])


# ─── Response Schemas ────────────────────────────────────────────────────────

class UserSearchResult(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    playlists: List[PlaylistResponse]
    users: List[UserSearchResult]
    playlists_count: int
    users_count: int


# ─── Endpoint ────────────────────────────────────────────────────────────────

@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query string"),
    type: Literal["all", "playlists", "users"] = Query(
        "all", description="Which entities to search: all | playlists | users"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unified global search.

    Rules:
      - Minimum 2 characters required (rejects "a", "", etc.)
      - Results cap: playlists top 10, users top 5
      - Playlists: ranked by PostgreSQL ts_rank with column weights (A-D)
        + engagement tiebreaker: (ts_rank*100) + (likes*0.1) + (views*0.05)
      - Users: tiered ranking — exact match > prefix > contains, ties broken by followers_count
    """
    # ── Guard: minimum query length ──────────────────────────────────────────
    q = q.strip()
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters long.",
        )

    playlists = []
    users = []

    # ── Playlist search ──────────────────────────────────────────────────────
    if type in ("all", "playlists"):
        raw_playlists = await PlaylistCRUD.search_playlists(db, q, limit=10)

        # Resolve interaction flags for the current user
        from sqlalchemy import select
        from models.playlist_like import PlaylistLike
        from models.playlist_save import PlaylistSave

        playlist_ids = [p.id for p in raw_playlists]

        liked_ids: set = set()
        saved_ids: set = set()

        if playlist_ids:
            liked_result = await db.execute(
                select(PlaylistLike.playlist_id).where(
                    PlaylistLike.user_id == current_user.id,
                    PlaylistLike.playlist_id.in_(playlist_ids),
                )
            )
            liked_ids = {row[0] for row in liked_result.fetchall()}

            saved_result = await db.execute(
                select(PlaylistSave.playlist_id).where(
                    PlaylistSave.user_id == current_user.id,
                    PlaylistSave.playlist_id.in_(playlist_ids),
                )
            )
            saved_ids = {row[0] for row in saved_result.fetchall()}

        for p in raw_playlists:
            pdict = {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "thumbnail": p.thumbnail,
                "is_public": p.is_public,
                "owner_id": p.owner_id,
                "owner_username": p.owner.username if p.owner else None,
                "video_count": p.video_count,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "category": p.category,
                "scenario": p.scenario,
                "vibes": p.vibes,
                "hook_description": p.hook_description,
                "likes_count": p.likes_count,
                "saves_count": p.saves_count,
                "views_count": p.views_count,
                "total_duration": p.total_duration,
                "is_featured": p.is_featured,
                "is_liked_by_me": p.id in liked_ids,
                "is_saved_by_me": p.id in saved_ids,
            }
            playlists.append(PlaylistResponse(**pdict))

    # ── User search ──────────────────────────────────────────────────────────
    if type in ("all", "users"):
        raw_users = await UserCRUD.search_users(db, q, limit=5)
        users = [UserSearchResult.model_validate(u) for u in raw_users]

    return SearchResponse(
        query=q,
        playlists=playlists,
        users=users,
        playlists_count=len(playlists),
        users_count=len(users),
    )
