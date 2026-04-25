from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, cast, Float
from sqlalchemy.orm import selectinload
from models.playlist import Playlist
from models.video import Video
from schemas.playlist import PlaylistCreate, PlaylistUpdate
from typing import Optional, List, Tuple


class PlaylistCRUD:

    @staticmethod
    async def create(db: AsyncSession, playlist_data: PlaylistCreate, owner_id: int) -> Playlist:
        """Create a new playlist with optional tag fields."""
        new_playlist = Playlist(
            title            = playlist_data.title,
            description      = playlist_data.description,
            thumbnail        = playlist_data.thumbnail,
            is_public        = playlist_data.is_public,
            owner_id         = owner_id,
            category         = playlist_data.category,
            scenario         = playlist_data.scenario,
            vibes            = playlist_data.vibes,
            hook_description = playlist_data.hook_description,
        )
        db.add(new_playlist)
        await db.commit()
        return await PlaylistCRUD.get_by_id(db, new_playlist.id)

    @staticmethod
    async def get_by_id(db: AsyncSession, playlist_id: int) -> Optional[Playlist]:
        """Get a playlist by ID, eagerly loading videos and owner."""
        result = await db.execute(
            select(Playlist)
            .options(selectinload(Playlist.videos), selectinload(Playlist.owner))
            .where(Playlist.id == playlist_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_playlists(db: AsyncSession, user_id: int) -> List[Playlist]:
        """Get all playlists owned by a specific user, newest first."""
        result = await db.execute(
            select(Playlist)
            .options(selectinload(Playlist.videos), selectinload(Playlist.owner))
            .where(Playlist.owner_id == user_id)
            .order_by(Playlist.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, playlist_id: int, playlist_data: PlaylistUpdate) -> Optional[Playlist]:
        """Update playlist — only fields that were actually sent are changed."""
        playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
        if not playlist:
            return None

        update_data = playlist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(playlist, field, value)

        await db.commit()
        return await PlaylistCRUD.get_by_id(db, playlist.id)

    @staticmethod
    async def delete(db: AsyncSession, playlist_id: int) -> bool:
        """Delete a playlist (cascades to videos, likes, saves)."""
        playlist = await PlaylistCRUD.get_by_id(db, playlist_id)
        if not playlist:
            return False
        await db.delete(playlist)
        await db.commit()
        return True

    # ── Feed ──────────────────────────────────────────────────────────────

    @staticmethod
    async def get_feed(
        db:              AsyncSession,
        current_user_id: int,
        page:            int = 1,
        page_size:       int = 20,
        category:        Optional[str] = None,
        scenario:        Optional[str] = None,
        vibes:           Optional[List[str]] = None,
        sort:            str = "popular",
    ) -> Tuple[List[Playlist], int]:
        """
        Paginated feed of public playlists, excluding the requesting user's own.
        Returns (playlists, total_count).
        """
        query = (
            select(Playlist)
            .where(
                Playlist.is_public == True,
                Playlist.owner_id  != current_user_id,
            )
            .options(selectinload(Playlist.videos), selectinload(Playlist.owner))
        )

        if category:
            query = query.where(Playlist.category == category)
        if scenario:
            query = query.where(Playlist.scenario == scenario)
        if vibes:
            # Match playlists that contain ANY of the requested vibes (PostgreSQL jsonb_path_exists)
            for vibe in vibes:
                query = query.where(
                    func.jsonb_path_exists(Playlist.vibes, f'$[*] ? (@ == "{vibe}")')
                )

        if sort == "recent":
            query = query.order_by(Playlist.created_at.desc())
        elif sort == "trending":
            days_old      = func.greatest(1, extract("epoch", func.now() - Playlist.created_at) / 86400)
            trending_score = cast(Playlist.likes_count, Float) / days_old
            query = query.order_by(trending_score.desc())
        else:  # popular (default)
            query = query.order_by(Playlist.likes_count.desc(), Playlist.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()

        offset = (page - 1) * page_size
        result = await db.execute(query.limit(page_size).offset(offset))
        return result.scalars().all(), total

    @staticmethod
    async def search_playlists(
        db:    AsyncSession,
        query: str,
        limit: int = 10,
    ) -> List[Playlist]:
        """
        Full-text search over public playlists using PostgreSQL ts_rank.
        Column weights:
          A (1.0) — title
          B (0.4) — category, scenario, vibes
          C (0.2) — hook_description
          D (0.1) — description
        Final score = (ts_rank * 100) + (likes * 0.1) + (views * 0.05)
        """
        import re
        from sqlalchemy import literal_column, cast, Text

        ts_vec = (
            func.setweight(
                func.to_tsvector(literal_column("'english'"), func.coalesce(Playlist.title, "")),
                literal_column("'A'"),
            )
            .op("||")(
                func.setweight(
                    func.to_tsvector(
                        literal_column("'english'"),
                        func.concat_ws(
                            " ",
                            func.coalesce(Playlist.category, ""),
                            func.coalesce(Playlist.scenario, ""),
                            func.coalesce(cast(Playlist.vibes, Text), ""),
                        ),
                    ),
                    literal_column("'B'"),
                )
            )
            .op("||")(
                func.setweight(
                    func.to_tsvector(
                        literal_column("'english'"),
                        func.coalesce(Playlist.hook_description, ""),
                    ),
                    literal_column("'C'"),
                )
            )
            .op("||")(
                func.setweight(
                    func.to_tsvector(
                        literal_column("'english'"),
                        func.coalesce(Playlist.description, ""),
                    ),
                    literal_column("'D'"),
                )
            )
        )

        raw_tokens = [re.sub(r"[^\w]", "", t) for t in query.split()]
        tokens = [t for t in raw_tokens if t]
        if not tokens:
            return []

        ts_query_str = " & ".join(f"{t}:*" for t in tokens)
        ts_query     = func.to_tsquery(literal_column("'english'"), ts_query_str)

        rank  = func.ts_rank(ts_vec, ts_query)
        score = (rank * 100) + (Playlist.likes_count * 0.1) + (Playlist.views_count * 0.05)

        stmt = (
            select(Playlist)
            .options(selectinload(Playlist.owner), selectinload(Playlist.videos))
            .where(Playlist.is_public == True, ts_vec.op("@@")(ts_query))
            .order_by(score.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()