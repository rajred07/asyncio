from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, async_session_maker
from crud.playlist import PlaylistCRUD
from crud.video import VideoCRUD
from crud.playlist_interactions import PlaylistInteractionsCRUD
from schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistResponse
from schemas.video import VideoCreate, VideoUpdate, VideoResponse
from schemas.interactions import LikeResponse, SaveResponse
from schemas.feed import FeedResponse, FeedFilters
from crud.feed import FeedCRUD
from utils.auth import get_current_active_user
from utils.youtube import get_video_metadata
from utils.background_tasks import import_playlist_simple
from utils.rate_limiter import rate_limit
from models.user import User
from typing import List, Optional
import math


router = APIRouter(prefix="/api/playlists", tags=["playlists"])

# ── Helpers ────────────────────────────────────────────────────────────────

def _playlist_to_dict(playlist, interactions: dict) -> dict:
    """Convert a Playlist ORM object + interaction flags to a response dict."""
    return {
        "id":               playlist.id,
        "title":            playlist.title,
        "description":      playlist.description,
        "thumbnail":        playlist.thumbnail,
        "is_public":        playlist.is_public,
        "owner_id":         playlist.owner_id,
        "owner_username":   playlist.owner_username,
        "video_count":      playlist.video_count,
        "created_at":       playlist.created_at,
        "updated_at":       playlist.updated_at,
        "category":         playlist.category,
        "scenario":         playlist.scenario,
        "vibes":            playlist.vibes,
        "hook_description": playlist.hook_description,
        "likes_count":      playlist.likes_count,
        "saves_count":      playlist.saves_count,
        "views_count":      playlist.views_count,
        "total_duration":   playlist.total_duration,
        "is_featured":      getattr(playlist, "is_featured", False),
        "is_liked_by_me":   interactions["is_liked"],
        "is_saved_by_me":   interactions["is_saved"],
    }


# ── Playlist CRUD ──────────────────────────────────────────────────────────

@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user:  User             = Depends(rate_limit("create_playlist", 30, 60)),
    db:            AsyncSession     = Depends(get_db),
):
    """Create a new playlist (rate-limited: 30 per minute)."""
    playlist = await PlaylistCRUD.create(db, playlist_data, current_user.id)
    return playlist


@router.get("/my", response_model=List[PlaylistResponse])
async def get_my_playlists(
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Get all playlists owned by the current user."""
    return await PlaylistCRUD.get_user_playlists(db, current_user.id)


@router.get("/liked", response_model=List[PlaylistResponse])
async def get_my_liked_playlists(
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Get all playlists liked by the current user."""
    playlists = await PlaylistInteractionsCRUD.get_liked_playlists(db, current_user.id)
    result = []
    for p in playlists:
        interactions = await PlaylistInteractionsCRUD.check_user_interactions(db, p.id, current_user.id)
        result.append(_playlist_to_dict(p, interactions))
    return result


@router.get("/saved", response_model=List[PlaylistResponse])
async def get_my_saved_playlists(
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Get all playlists saved by the current user (personal library)."""
    playlists = await PlaylistInteractionsCRUD.get_saved_playlists(db, current_user.id)
    result = []
    for p in playlists:
        interactions = await PlaylistInteractionsCRUD.check_user_interactions(db, p.id, current_user.id)
        result.append(_playlist_to_dict(p, interactions))
    return result


# ── Feed Endpoints ─────────────────────────────────────────────────────────
# IMPORTANT: /feed/* routes must be declared BEFORE /{playlist_id} to avoid
# FastAPI treating "feed" as a playlist ID.

@router.get("/feed", response_model=FeedResponse)
async def get_playlist_feed(
    page:         int            = 1,
    page_size:    int            = 20,
    category:     Optional[str] = None,
    scenario:     Optional[str] = None,
    vibes:        Optional[str] = None,   # comma-separated: "Lo-Fi/Beats,Instrumental"
    sort:         str            = "popular",  # popular | recent | trending
    current_user: User           = Depends(get_current_active_user),
    db:           AsyncSession   = Depends(get_db),
):
    """
    Paginated public feed with optional tag filters.
    - category: Gaming | Entertainment | Education | Music
    - scenario: e.g. Meal Time, High Focus, Workout
    - vibes: comma-separated e.g. "Lo-Fi/Beats,Instrumental"
    - sort: popular | recent | trending
    """
    page_size = max(1, min(page_size, 50))
    page      = max(1, page)
    if sort not in ("popular", "recent", "trending"):
        sort = "popular"

    vibes_list = [v.strip() for v in vibes.split(",") if v.strip()] if vibes else None

    playlists, total = await PlaylistCRUD.get_feed(
        db=db,
        current_user_id=current_user.id,
        page=page, page_size=page_size,
        category=category, scenario=scenario, vibes=vibes_list, sort=sort,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    result_playlists = []
    for p in playlists:
        interactions = await PlaylistInteractionsCRUD.check_user_interactions(db, p.id, current_user.id)
        result_playlists.append(_playlist_to_dict(p, interactions))

    active_filters = FeedFilters(category=category, scenario=scenario, vibes=vibes_list) \
        if (category or scenario or vibes_list) else None

    return {
        "playlists":   result_playlists,
        "total":       total,
        "page":        page,
        "page_size":   page_size,
        "total_pages": total_pages,
        "has_next":    page < total_pages,
        "has_prev":    page > 1,
        "sort":        sort,
        "filters":     active_filters,
    }


@router.get("/feed/for-you")
async def for_you_feed(
    page:         int            = 1,
    page_size:    int            = 20,
    category:     Optional[str] = None,
    duration:     Optional[str] = None,   # quick | medium | long
    current_user: User           = Depends(get_current_active_user),
    db:           AsyncSession   = Depends(get_db),
):
    """
    Personalised feed sorted by engagement score.
    Playlists matching the user's preferred_categories get a 1.5× boost.
    """
    return await FeedCRUD.get_for_you_feed(
        db, current_user,
        page=page, page_size=page_size,
        category=category, duration=duration,
    )


@router.get("/feed/following")
async def following_feed(
    page:         int          = 1,
    page_size:    int          = 20,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Chronological feed of playlists from users the current user follows."""
    return await FeedCRUD.get_following_feed(db, current_user, page=page, page_size=page_size)


@router.get("/feed/trending")
async def trending_feed(
    page:         int            = 1,
    page_size:    int            = 20,
    category:     Optional[str] = None,
    current_user: User           = Depends(get_current_active_user),
    db:           AsyncSession   = Depends(get_db),
):
    """
    Playlists ranked by 24-hour rolling engagement.
    trending_score = recent_likes×2 + recent_saves×3
    """
    return await FeedCRUD.get_trending_feed(db, page=page, page_size=page_size, category=category)


@router.get("/feed/sections")
async def feed_sections(
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """
    All 4 horizontal-scroll sections for the For You tab in one request:
    - editors_picks: admin-curated featured playlists
    - trending_now: top 5 by 24h engagement
    - because_you_liked: similar to last liked playlist
    - new_and_rising: < 48h old, above-average likes
    """
    return await FeedCRUD.get_sections(db, current_user)


# ── Playlist by ID ─────────────────────────────────────────────────────────

@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(
    playlist_id:  int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Get a playlist by ID with per-user interaction flags."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist.is_public and playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    interactions = await PlaylistInteractionsCRUD.check_user_interactions(db, playlist_id, current_user.id)
    return _playlist_to_dict(playlist, interactions)


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id:   int,
    playlist_data: PlaylistUpdate,
    current_user:  User         = Depends(get_current_active_user),
    db:            AsyncSession = Depends(get_db),
):
    """Update a playlist (owner only). Tag fields can be updated individually."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can update this playlist")

    return await PlaylistCRUD.update(db, playlist_id, playlist_data)


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id:  int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Delete a playlist (owner only)."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this playlist")

    await PlaylistCRUD.delete(db, playlist_id)


# ── Interaction Endpoints ──────────────────────────────────────────────────

@router.post("/{playlist_id}/like", response_model=LikeResponse)
async def like_playlist(
    playlist_id:  int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Toggle like on a public playlist."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist.is_public:
        raise HTTPException(status_code=403, detail="Cannot like a private playlist")

    try:
        is_liked, likes_count = await PlaylistInteractionsCRUD.toggle_like(db, playlist_id, current_user.id)
        return {"liked": is_liked, "likes_count": likes_count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{playlist_id}/save", response_model=SaveResponse)
async def save_playlist(
    playlist_id:  int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Toggle save on a playlist (add/remove from personal library)."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist.is_public and playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        is_saved, saves_count = await PlaylistInteractionsCRUD.toggle_save(db, playlist_id, current_user.id)
        return {"saved": is_saved, "saves_count": saves_count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{playlist_id}/view")
async def record_playlist_view(
    playlist_id:  int,
    request:      Request,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """
    Record a playlist view with IP-based deduplication.
    Same IP viewing the same playlist within 1 hour counts as 1 view.
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import update as sa_update, select as sa_select
    from models.playlist import Playlist as PlaylistModel
    from models.playlist_view import PlaylistView

    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist.is_public and playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    viewer_ip = request.headers.get("X-Forwarded-For", request.client.host)
    if viewer_ip:
        viewer_ip = viewer_ip.split(",")[0].strip()

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    already_viewed = await db.execute(
        sa_select(PlaylistView).where(
            PlaylistView.playlist_id == playlist_id,
            PlaylistView.viewer_ip   == viewer_ip,
            PlaylistView.viewed_at   >= one_hour_ago,
        )
    )
    if already_viewed.scalar_one_or_none() is not None:
        return {"counted": False, "message": "Already viewed recently"}

    db.add(PlaylistView(playlist_id=playlist_id, viewer_ip=viewer_ip))
    await db.execute(
        sa_update(PlaylistModel)
        .where(PlaylistModel.id == playlist_id)
        .values(views_count=PlaylistModel.views_count + 1)
    )
    await db.commit()
    return {"counted": True, "message": "View recorded"}


# ── Video Management ───────────────────────────────────────────────────────

@router.post(
    "/{playlist_id}/videos/youtube",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_video_from_youtube(
    playlist_id:      int,
    youtube_url:      str,
    user_description: str          = None,
    current_user:     User         = Depends(rate_limit("add_video", 3, 60)),
    db:               AsyncSession = Depends(get_db),
):
    """Add a video to a playlist via YouTube URL (owner only, rate-limited: 3/min)."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the playlist owner can add videos")

    try:
        video_data = await get_video_metadata(youtube_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if await VideoCRUD.check_duplicate(db, playlist_id, video_data["youtube_id"]):
        raise HTTPException(status_code=400, detail="Video already exists in this playlist")

    video_create = VideoCreate(**video_data, user_description=user_description, position=0)
    return await VideoCRUD.create(db, video_create, playlist_id, current_user.id)


@router.get("/{playlist_id}/videos", response_model=List[VideoResponse])
async def get_playlist_videos(
    playlist_id:  int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Get all videos in a playlist."""
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist.is_public and playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await VideoCRUD.get_playlist_videos(db, playlist_id)


@router.put("/videos/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id:     int,
    video_data:   VideoUpdate,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Update a video's description or position (owner only)."""
    video = await VideoCRUD.get_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    playlist = await PlaylistCRUD.get_by_id(db, video.playlist_id)
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the playlist owner can update videos")
    return await VideoCRUD.update(db, video_id, video_data)


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id:     int,
    current_user: User         = Depends(get_current_active_user),
    db:           AsyncSession = Depends(get_db),
):
    """Remove a video from a playlist (owner only)."""
    video = await VideoCRUD.get_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    playlist = await PlaylistCRUD.get_by_id(db, video.playlist_id)
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the playlist owner can delete videos")
    await VideoCRUD.delete(db, video_id)


@router.post("/{playlist_id}/videos/import-playlist")
async def import_youtube_playlist(
    playlist_id:          int,
    youtube_playlist_url: str,
    max_videos:           int            = 50,
    background_tasks:     BackgroundTasks = None,
    current_user:         User            = Depends(rate_limit("import_playlist", 5, 3600)),
    db:                   AsyncSession    = Depends(get_db),
):
    """
    Bulk import a YouTube playlist (owner only).
    Runs in the background — rate-limited to 5 imports per hour.
    """
    playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can import")

    async def run_import():
        async with async_session_maker() as new_db:
            await import_playlist_simple(new_db, playlist_id, youtube_playlist_url, current_user.id, max_videos)

    background_tasks.add_task(run_import)
    return {"message": "Import started", "max_videos": max_videos}
