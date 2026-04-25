from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.video import Video
from models.playlist import Playlist
from schemas.video import VideoCreate, VideoUpdate
from typing import Optional, List

class VideoCRUD:
    @staticmethod
    async def create(db: AsyncSession, video_data: VideoCreate, playlist_id: int, added_by_id: int) -> Video:
        """Add video to playlist and update cached counters"""
        new_video = Video(
            youtube_id=video_data.youtube_id,
            title=video_data.title,
            channel_name=video_data.channel_name,
            thumbnail=video_data.thumbnail,
            views=video_data.views,
            duration=video_data.duration,
            youtube_description=video_data.youtube_description,
            user_description=video_data.user_description,
            position=video_data.position,
            playlist_id=playlist_id,
            added_by_id=added_by_id
        )
        
        db.add(new_video)
        
        # ========== Update parent playlist cached counters + thumbnail ==========
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        if playlist:
            playlist.video_count += 1
            playlist.total_duration += (video_data.duration or 0)
            
            # Auto-set thumbnail from first video if playlist has none
            if not playlist.thumbnail and video_data.thumbnail:
                playlist.thumbnail = video_data.thumbnail
        # =========================================================================
        
        await db.commit()
        await db.refresh(new_video)
        return new_video
    
    @staticmethod
    async def get_by_id(db: AsyncSession, video_id: int) -> Optional[Video]:
        """Get video by ID"""
        result = await db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_playlist_videos(db: AsyncSession, playlist_id: int) -> List[Video]:
        """Get all videos in a playlist"""
        result = await db.execute(
            select(Video)
            .where(Video.playlist_id == playlist_id)
            .order_by(Video.position, Video.created_at)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, video_id: int, video_data: VideoUpdate) -> Optional[Video]:
        """Update video (user description, position)"""
        video = await VideoCRUD.get_by_id(db, video_id)
        if not video:
            return None
        
        update_data = video_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(video, field, value)
        
        await db.commit()
        await db.refresh(video)
        return video
    
    @staticmethod
    async def delete(db: AsyncSession, video_id: int) -> bool:
        """Remove video from playlist and update cached counters"""
        video = await VideoCRUD.get_by_id(db, video_id)
        if not video:
            return False
        
        # ========== Update parent playlist cached counters + thumbnail ==========
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == video.playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        if playlist:
            playlist.video_count    = max(0, playlist.video_count - 1)
            playlist.total_duration = max(0, playlist.total_duration - (video.duration or 0))
            
            # If this video's thumbnail was the playlist thumbnail, re-derive from new first video
            if playlist.thumbnail == video.thumbnail:
                next_video_result = await db.execute(
                    select(Video)
                    .where(Video.playlist_id == video.playlist_id, Video.id != video.id)
                    .order_by(Video.position, Video.created_at)
                    .limit(1)
                )
                next_video = next_video_result.scalar_one_or_none()
                playlist.thumbnail = next_video.thumbnail if next_video else None
        # =========================================================================
        
        await db.delete(video)
        await db.commit()
        return True
    
    @staticmethod
    async def check_duplicate(db: AsyncSession, playlist_id: int, youtube_id: str) -> bool:
        """Check if video already exists in playlist"""
        result = await db.execute(
            select(Video)
            .where(Video.playlist_id == playlist_id, Video.youtube_id == youtube_id)
        )
        return result.scalar_one_or_none() is not None