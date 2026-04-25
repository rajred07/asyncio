from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from models.playlist import Playlist
from models.playlist_like import PlaylistLike
from models.playlist_save import PlaylistSave
from typing import Tuple, Dict, List

class PlaylistInteractionsCRUD:
    
    @staticmethod
    async def toggle_like(db: AsyncSession, playlist_id: int, user_id: int) -> Tuple[bool, int]:
        """
        Toggle like on a playlist
        Returns: (is_liked_after_toggle, total_likes_count)
        """
        # Check if already liked
        result = await db.execute(
            select(PlaylistLike).where(
                PlaylistLike.playlist_id == playlist_id,
                PlaylistLike.user_id == user_id
            )
        )
        existing_like = result.scalar_one_or_none()
        
        # Get the playlist
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        
        if not playlist:
            raise ValueError("Playlist not found")
        
        if existing_like:
            # Unlike: Remove like and decrement counter
            await db.delete(existing_like)
            playlist.likes_count = max(0, playlist.likes_count - 1)
            await db.commit()
            return False, playlist.likes_count
        else:
            # Like: Add like and increment counter
            new_like = PlaylistLike(
                user_id=user_id,
                playlist_id=playlist_id
            )
            db.add(new_like)
            playlist.likes_count += 1
            await db.commit()
            return True, playlist.likes_count
    
    @staticmethod
    async def toggle_save(db: AsyncSession, playlist_id: int, user_id: int) -> Tuple[bool, int]:
        """
        Toggle save on a playlist
        Returns: (is_saved_after_toggle, total_saves_count)
        """
        # Check if already saved
        result = await db.execute(
            select(PlaylistSave).where(
                PlaylistSave.playlist_id == playlist_id,
                PlaylistSave.user_id == user_id
            )
        )
        existing_save = result.scalar_one_or_none()
        
        # Get the playlist
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        
        if not playlist:
            raise ValueError("Playlist not found")
        
        if existing_save:
            # Unsave: Remove save and decrement counter
            await db.delete(existing_save)
            playlist.saves_count = max(0, playlist.saves_count - 1)
            await db.commit()
            return False, playlist.saves_count
        else:
            # Save: Add save and increment counter
            new_save = PlaylistSave(
                user_id=user_id,
                playlist_id=playlist_id
            )
            db.add(new_save)
            playlist.saves_count += 1
            await db.commit()
            return True, playlist.saves_count
    
    @staticmethod
    async def check_user_interactions(db: AsyncSession, playlist_id: int, user_id: int) -> Dict[str, bool]:
        """
        Check if user has liked/saved a playlist
        Returns: {"is_liked": bool, "is_saved": bool}
        """
        # Check like
        like_result = await db.execute(
            select(PlaylistLike).where(
                PlaylistLike.playlist_id == playlist_id,
                PlaylistLike.user_id == user_id
            )
        )
        is_liked = like_result.scalar_one_or_none() is not None
        
        # Check save
        save_result = await db.execute(
            select(PlaylistSave).where(
                PlaylistSave.playlist_id == playlist_id,
                PlaylistSave.user_id == user_id
            )
        )
        is_saved = save_result.scalar_one_or_none() is not None
        
        return {"is_liked": is_liked, "is_saved": is_saved}
    
    @staticmethod
    async def get_liked_playlists(db: AsyncSession, user_id: int) -> List[Playlist]:
        """Get all playlists liked by user"""
        result = await db.execute(
            select(Playlist)
            .join(PlaylistLike, PlaylistLike.playlist_id == Playlist.id)
            .where(PlaylistLike.user_id == user_id)
            .options(selectinload(Playlist.videos), selectinload(Playlist.owner))
            .order_by(PlaylistLike.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_saved_playlists(db: AsyncSession, user_id: int) -> List[Playlist]:
        """Get all playlists saved by user (user's library)"""
        result = await db.execute(
            select(Playlist)
            .join(PlaylistSave, PlaylistSave.playlist_id == Playlist.id)
            .where(PlaylistSave.user_id == user_id)
            .options(selectinload(Playlist.videos), selectinload(Playlist.owner))
            .order_by(PlaylistSave.saved_at.desc())
        )
        return result.scalars().all()