# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from models.group_video import GroupPlaylistVideo
# from schemas.group_video import GroupVideoCreate, GroupVideoUpdate
# from typing import Optional, List

# class GroupVideoCRUD:
    
#     @staticmethod
#     async def create(
#         db: AsyncSession,
#         playlist_id: int,
#         video_data: GroupVideoCreate,
#         added_by_id: int
#     ) -> GroupPlaylistVideo:
#         """Add a video to group playlist"""
#         new_video = GroupPlaylistVideo(
#             group_playlist_id=playlist_id,
#             youtube_id=video_data.youtube_id,
#             title=video_data.title,
#             channel_name=video_data.channel_name,
#             thumbnail=video_data.thumbnail,
#             views=video_data.views,
#             youtube_description=video_data.youtube_description,
#             user_description=video_data.user_description,
#             position=video_data.position,
#             added_by_id=added_by_id
#         )
        
#         db.add(new_video)
#         await db.commit()
#         await db.refresh(new_video)
#         return new_video
    
#     @staticmethod
#     async def get_by_id(
#         db: AsyncSession,
#         video_id: int,
#         load_added_by: bool = False
#     ) -> Optional[GroupPlaylistVideo]:
#         """Get video by ID"""
#         query = select(GroupPlaylistVideo).where(GroupPlaylistVideo.id == video_id)
        
#         if load_added_by:
#             query = query.options(selectinload(GroupPlaylistVideo.added_by))
        
#         result = await db.execute(query)
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_playlist_videos(
#         db: AsyncSession,
#         playlist_id: int
#     ) -> List[GroupPlaylistVideo]:
#         """Get all videos in a group playlist"""
#         result = await db.execute(
#             select(GroupPlaylistVideo)
#             .options(selectinload(GroupPlaylistVideo.added_by))
#             .where(GroupPlaylistVideo.group_playlist_id == playlist_id)
#             .order_by(GroupPlaylistVideo.position.asc(), GroupPlaylistVideo.created_at.asc())
#         )
#         return result.scalars().all()
    
#     @staticmethod
#     async def update(
#         db: AsyncSession,
#         video_id: int,
#         video_data: GroupVideoUpdate
#     ) -> Optional[GroupPlaylistVideo]:
#         """Update video details"""
#         video = await GroupVideoCRUD.get_by_id(db, video_id)
#         if not video:
#             return None
        
#         update_data = video_data.model_dump(exclude_unset=True)
#         for field, value in update_data.items():
#             setattr(video, field, value)
        
#         await db.commit()
#         await db.refresh(video)
#         return video
    
#     @staticmethod
#     async def delete(db: AsyncSession, video_id: int) -> bool:
#         """Delete a video from group playlist"""
#         video = await GroupVideoCRUD.get_by_id(db, video_id)
#         if not video:
#             return False
        
#         await db.delete(video)
#         await db.commit()
#         return True
    
#     @staticmethod
#     async def get_videos_by_user(
#         db: AsyncSession,
#         playlist_id: int,
#         user_id: int
#     ) -> List[GroupPlaylistVideo]:
#         """Get all videos added by a specific user in a playlist"""
#         result = await db.execute(
#             select(GroupPlaylistVideo)
#             .where(
#                 GroupPlaylistVideo.group_playlist_id == playlist_id,
#                 GroupPlaylistVideo.added_by_id == user_id
#             )
#             .order_by(GroupPlaylistVideo.created_at.desc())
#         )
#         return result.scalars().all()



from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from models.group_video import GroupPlaylistVideo
from schemas.group_video import GroupVideoCreate, GroupVideoUpdate
from typing import Optional, List

class GroupVideoCRUD:
    
    @staticmethod
    async def create(
        db: AsyncSession,
        playlist_id: int,
        video_data: GroupVideoCreate,
        added_by_id: int
    ) -> GroupPlaylistVideo:
        """Add a video to group playlist"""
        new_video = GroupPlaylistVideo(
            group_playlist_id=playlist_id,
            youtube_id=video_data.youtube_id,
            title=video_data.title,
            channel_name=video_data.channel_name,
            thumbnail=video_data.thumbnail,
            views=video_data.views,
            youtube_description=video_data.youtube_description,
            user_description=video_data.user_description,
            position=video_data.position,
            added_by_id=added_by_id
        )
        
        db.add(new_video)
        await db.commit()
        await db.refresh(new_video)
        return new_video
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        video_id: int,
        load_added_by: bool = False
    ) -> Optional[GroupPlaylistVideo]:
        """Get video by ID"""
        query = select(GroupPlaylistVideo).where(GroupPlaylistVideo.id == video_id)
        
        if load_added_by:
            query = query.options(selectinload(GroupPlaylistVideo.added_by))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_playlist_videos(
        db: AsyncSession,
        playlist_id: int
    ) -> List[GroupPlaylistVideo]:
        """Get all videos in a group playlist"""
        result = await db.execute(
            select(GroupPlaylistVideo)
            .options(selectinload(GroupPlaylistVideo.added_by))
            .where(GroupPlaylistVideo.group_playlist_id == playlist_id)
            .order_by(GroupPlaylistVideo.position.asc(), GroupPlaylistVideo.created_at.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession,
        video_id: int,
        video_data: GroupVideoUpdate
    ) -> Optional[GroupPlaylistVideo]:
        """Update video details"""
        video = await GroupVideoCRUD.get_by_id(db, video_id)
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
        """Delete a video from group playlist"""
        video = await GroupVideoCRUD.get_by_id(db, video_id)
        if not video:
            return False
        
        await db.delete(video)
        await db.commit()
        return True
    
    @staticmethod
    async def get_videos_by_user(
        db: AsyncSession,
        playlist_id: int,
        user_id: int
    ) -> List[GroupPlaylistVideo]:
        """Get all videos added by a specific user in a playlist"""
        result = await db.execute(
            select(GroupPlaylistVideo)
            .where(
                GroupPlaylistVideo.group_playlist_id == playlist_id,
                GroupPlaylistVideo.added_by_id == user_id
            )
            .order_by(GroupPlaylistVideo.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def check_duplicate(
        db: AsyncSession,
        playlist_id: int,
        youtube_id: str
    ) -> bool:
        """Check if video already exists in group playlist"""
        result = await db.execute(
            select(GroupPlaylistVideo)
            .where(
                and_(
                    GroupPlaylistVideo.group_playlist_id == playlist_id,
                    GroupPlaylistVideo.youtube_id == youtube_id
                )
            )
        )
        return result.scalar_one_or_none() is not None