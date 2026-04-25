"""
Feed CRUD — all feed query logic lives here.
Follows the same async SQLAlchemy pattern as the rest of the codebase.

Score formula (inline, no stored column):
    score = (likes_count * 2) + (saves_count * 3) + (views_count * 0.5)

Preference boost (For You):
    If user has preferred_categories → matching playlists score × 1.5
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List

from sqlalchemy import select, func, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.playlist      import Playlist
from models.playlist_like import PlaylistLike
from models.playlist_save import PlaylistSave
from models.user          import User, followers_table
from utils.cache          import get_feed_cache, set_feed_cache


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _score_expr():
    """Inline engagement score: likes×2 + saves×3 + views×0.5"""
    return (
        Playlist.likes_count * 2 +
        Playlist.saves_count * 3 +
        (Playlist.views_count * 0.5)
    )


def _apply_duration_filter(query, duration: Optional[str]):
    """Add duration filter to an existing query."""
    if duration == "quick":
        query = query.where(Playlist.total_duration < 1800)          # < 30 min
    elif duration == "medium":
        query = query.where(Playlist.total_duration.between(1800, 7200))  # 30 min – 2 hr
    elif duration == "long":
        query = query.where(Playlist.total_duration > 7200)           # > 2 hr
    return query


def _apply_category_filter(query, category: Optional[str]):
    if category:
        query = query.where(Playlist.category == category)
    return query


def _build_playlist_dict(p: Playlist, is_liked: bool = False, is_saved: bool = False) -> dict:
    """Convert a Playlist ORM object to a response dict."""
    return {
        "id":               p.id,
        "title":            p.title,
        "description":      p.description,
        "thumbnail":        p.thumbnail,
        "is_public":        p.is_public,
        "owner_id":         p.owner_id,
        "owner_username":   p.owner_username,
        "video_count":      p.video_count,
        "created_at":       p.created_at,
        "updated_at":       p.updated_at,
        "category":         p.category,
        "scenario":         p.scenario,
        "vibes":            p.vibes,
        "hook_description": p.hook_description,
        "likes_count":      p.likes_count,
        "saves_count":      p.saves_count,
        "views_count":      p.views_count,
        "total_duration":   p.total_duration,
        "is_featured":      p.is_featured,
        "is_liked_by_me":   is_liked,
        "is_saved_by_me":   is_saved,
    }


# ---------------------------------------------------------------------------
# Tab 1: For You
# ---------------------------------------------------------------------------

class FeedCRUD:

    @staticmethod
    async def get_for_you_feed(
        db:              AsyncSession,
        current_user:    User,
        page:            int = 1,
        page_size:       int = 20,
        category:        Optional[str] = None,
        duration:        Optional[str] = None,  # "quick" | "medium" | "long"
    ) -> dict:
        """
        Personalized feed, score-sorted with optional preference boost.
        Excludes the user's own playlists. Results cached per user/page/filters.
        """
        # Build cache key — unique per user + pagination + filters
        cache_key = f"for_you:{current_user.id}:{page}:{category or ''}:{duration or ''}"
        cached = get_feed_cache(cache_key)
        if cached:
            return cached

        preferred_cats = current_user.preferred_categories or []

        # Build score expression — boost playlists in preferred categories × 1.5
        if preferred_cats:
            boosted_score = case(
                (Playlist.category.in_(preferred_cats), _score_expr() * 1.5),
                else_=_score_expr()
            )
        else:
            boosted_score = _score_expr()

        stmt = (
            select(Playlist)
            .where(
                Playlist.is_public == True,
                Playlist.owner_id  != current_user.id
            )
            .order_by(boosted_score.desc())
        )

        stmt = _apply_category_filter(stmt, category)
        stmt = _apply_duration_filter(stmt, duration)

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        # Paginate
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        playlists = (await db.execute(stmt)).scalars().all()

        result = {
            "playlists": [_build_playlist_dict(p) for p in playlists],
            "total":     total,
            "page":      page,
            "page_size": page_size,
        }
        set_feed_cache(cache_key, result)
        return result

    # -----------------------------------------------------------------------
    # Tab 2: Following
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_following_feed(
        db:           AsyncSession,
        current_user: User,
        page:         int = 1,
        page_size:    int = 20,
    ) -> dict:
        """
        Chronological playlists from users the current user follows.
        Cached per user+page for 5 minutes.
        """
        cache_key = f"following:{current_user.id}:{page}"
        cached = get_feed_cache(cache_key)
        if cached:
            return cached

        # Get IDs of people being followed
        following_stmt = select(followers_table.c.following_id).where(
            followers_table.c.follower_id == current_user.id
        )
        following_rows = (await db.execute(following_stmt)).all()
        following_ids  = [row[0] for row in following_rows]

        if not following_ids:
            return {
                "playlists": [],
                "total":     0,
                "page":      page,
                "page_size": page_size,
                "message":   "Follow people to see their playlists here",
            }

        stmt = (
            select(Playlist)
            .where(
                Playlist.owner_id.in_(following_ids),
                Playlist.is_public == True
            )
            .order_by(Playlist.created_at.desc())
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        playlists = (await db.execute(stmt)).scalars().all()

        result = {
            "playlists": [_build_playlist_dict(p) for p in playlists],
            "total":     total,
            "page":      page,
            "page_size": page_size,
        }
        set_feed_cache(cache_key, result)
        return result

    # -----------------------------------------------------------------------
    # Tab 3: Trending (24-hour rolling window)
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_trending_feed(
        db:        AsyncSession,
        page:      int = 1,
        page_size: int = 20,
        category:  Optional[str] = None,
    ) -> dict:
        """
        Playlists ranked by recent engagement in the last 24 hours.
        trending_score = recent_likes × 2 + recent_saves × 3
        Cached globally per page+category (same for all users).
        """
        cache_key = f"trending:{page}:{category or ''}"
        cached = get_feed_cache(cache_key)
        if cached:
            return cached

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        # Subquery: recent likes per playlist
        recent_likes = (
            select(
                PlaylistLike.playlist_id,
                func.count(PlaylistLike.id).label("recent_likes")
            )
            .where(PlaylistLike.created_at >= cutoff)
            .group_by(PlaylistLike.playlist_id)
            .subquery()
        )

        # Subquery: recent saves per playlist
        recent_saves = (
            select(
                PlaylistSave.playlist_id,
                func.count(PlaylistSave.id).label("recent_saves")
            )
            .where(PlaylistSave.saved_at >= cutoff)
            .group_by(PlaylistSave.playlist_id)
            .subquery()
        )

        trending_score = (
            func.coalesce(recent_likes.c.recent_likes, 0) * 2 +
            func.coalesce(recent_saves.c.recent_saves, 0) * 3
        )

        stmt = (
            select(Playlist, trending_score.label("trending_score"))
            .outerjoin(recent_likes, Playlist.id == recent_likes.c.playlist_id)
            .outerjoin(recent_saves, Playlist.id == recent_saves.c.playlist_id)
            .where(Playlist.is_public == True)
            .order_by(text("trending_score DESC"))
        )

        stmt = _apply_category_filter(stmt, category)

        count_stmt = select(func.count()).select_from(
            select(Playlist)
            .outerjoin(recent_likes, Playlist.id == recent_likes.c.playlist_id)
            .outerjoin(recent_saves, Playlist.id == recent_saves.c.playlist_id)
            .where(Playlist.is_public == True)
            .subquery()
        )
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = (await db.execute(stmt)).all()

        # Each row is (Playlist, trending_score) due to the labeled column
        playlists = [row[0] for row in rows]

        result = {
            "playlists": [_build_playlist_dict(p) for p in playlists],
            "total":     total,
            "page":      page,
            "page_size": page_size,
        }
        set_feed_cache(cache_key, result)
        return result

    # -----------------------------------------------------------------------
    # Horizontal Sections (all 4 in one request for For You page)
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_sections(
        db:           AsyncSession,
        current_user: User,
    ) -> dict:
        """
        Returns all horizontal scroll sections for the For You tab.
        Cached per user for 5 minutes — most expensive query in the feed.
        """
        cache_key = f"sections:{current_user.id}"
        cached = get_feed_cache(cache_key)
        if cached:
            return cached
        cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        cutoff_48h = datetime.now(timezone.utc) - timedelta(hours=48)

        # -- 1. Editor's Picks -----------------------------------------------
        editors_stmt = (
            select(Playlist)
            .where(Playlist.is_featured == True, Playlist.is_public == True)
            .order_by(_score_expr().desc())
            .limit(10)
        )
        editors_picks = (await db.execute(editors_stmt)).scalars().all()

        # -- 2. Trending Now (top 5 by 24h engagement) -----------------------
        recent_likes_sub = (
            select(
                PlaylistLike.playlist_id,
                func.count(PlaylistLike.id).label("rl")
            )
            .where(PlaylistLike.created_at >= cutoff_24h)
            .group_by(PlaylistLike.playlist_id)
            .subquery()
        )
        recent_saves_sub = (
            select(
                PlaylistSave.playlist_id,
                func.count(PlaylistSave.id).label("rs")
            )
            .where(PlaylistSave.saved_at >= cutoff_24h)
            .group_by(PlaylistSave.playlist_id)
            .subquery()
        )
        trending_stmt = (
            select(Playlist)
            .outerjoin(recent_likes_sub, Playlist.id == recent_likes_sub.c.playlist_id)
            .outerjoin(recent_saves_sub, Playlist.id == recent_saves_sub.c.playlist_id)
            .where(Playlist.is_public == True)
            .order_by(
                (func.coalesce(recent_likes_sub.c.rl, 0) * 2 +
                 func.coalesce(recent_saves_sub.c.rs, 0) * 3).desc()
            )
            .limit(5)
        )
        trending_now = (await db.execute(trending_stmt)).scalars().all()

        # -- 3. Because You Liked X ------------------------------------------
        because_source = None
        because_playlists: List[Playlist] = []

        last_like_stmt = (
            select(PlaylistLike)
            .where(PlaylistLike.user_id == current_user.id)
            .order_by(PlaylistLike.created_at.desc())
            .limit(1)
        )
        last_like = (await db.execute(last_like_stmt)).scalar_one_or_none()

        if last_like:
            source_stmt = select(Playlist).where(Playlist.id == last_like.playlist_id)
            because_source = (await db.execute(source_stmt)).scalar_one_or_none()

            if because_source:
                similar_stmt = (
                    select(Playlist)
                    .where(
                        Playlist.category  == because_source.category,
                        Playlist.id        != because_source.id,
                        Playlist.is_public == True,
                        Playlist.owner_id  != current_user.id,
                    )
                    .order_by(_score_expr().desc())
                    .limit(5)
                )
                because_playlists = (await db.execute(similar_stmt)).scalars().all()

        # -- 4. New & Rising -------------------------------------------------
        avg_likes_result = await db.execute(select(func.avg(Playlist.likes_count)))
        avg_likes = avg_likes_result.scalar_one() or 0

        new_rising_stmt = (
            select(Playlist)
            .where(
                Playlist.created_at >= cutoff_48h,
                Playlist.likes_count >= avg_likes,
                Playlist.is_public   == True,
            )
            .order_by(_score_expr().desc())
            .limit(5)
        )
        new_and_rising = (await db.execute(new_rising_stmt)).scalars().all()

        # -- Build response --------------------------------------------------
        result = {
            "editors_picks": [_build_playlist_dict(p) for p in editors_picks],
            "trending_now":  [_build_playlist_dict(p) for p in trending_now],
            "because_you_liked": {
                "source":    _build_playlist_dict(because_source) if because_source else None,
                "playlists": [_build_playlist_dict(p) for p in because_playlists],
            },
            "new_and_rising": [_build_playlist_dict(p) for p in new_and_rising],
        }
        set_feed_cache(cache_key, result)
        return result
