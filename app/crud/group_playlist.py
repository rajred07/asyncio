from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.group_playlist import GroupPlaylist
from models.group_member import GroupPlaylistMember, MemberRole
from schemas.group_playlist import GroupPlaylistCreate, GroupPlaylistUpdate
from typing import Optional, List

class GroupPlaylistCRUD:
    
    @staticmethod
    async def create(
        db: AsyncSession,
        playlist_data: GroupPlaylistCreate,
        owner_id: int
    ) -> GroupPlaylist:
        """Create a new group playlist and add owner as OWNER member"""
        # Create the playlist
        new_playlist = GroupPlaylist(
            title=playlist_data.title,
            description=playlist_data.description,
            thumbnail=playlist_data.thumbnail,
            owner_id=owner_id
        )
        
        db.add(new_playlist)
        await db.flush()  # Flush to get the ID
        
        # Add owner as OWNER member
        owner_member = GroupPlaylistMember(
            group_playlist_id=new_playlist.id,
            user_id=owner_id,
            role=MemberRole.OWNER
        )
        db.add(owner_member)
        
        await db.commit()
        await db.refresh(new_playlist)
        return new_playlist
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        playlist_id: int,
        load_members: bool = False,
        load_videos: bool = False
    ) -> Optional[GroupPlaylist]:
        """Get group playlist by ID with optional eager loading"""
        query = select(GroupPlaylist).where(GroupPlaylist.id == playlist_id)
        
        if load_members:
            query = query.options(selectinload(GroupPlaylist.members))
        if load_videos:
            query = query.options(selectinload(GroupPlaylist.videos))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_playlists(
        db: AsyncSession,
        user_id: int
    ) -> List[GroupPlaylist]:
        """Get all group playlists where user is a member"""
        result = await db.execute(
            select(GroupPlaylist)
            .join(GroupPlaylistMember)
            .where(GroupPlaylistMember.user_id == user_id)
            .order_by(GroupPlaylist.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_owned_playlists(
        db: AsyncSession,
        owner_id: int
    ) -> List[GroupPlaylist]:
        """Get all group playlists owned by user"""
        result = await db.execute(
            select(GroupPlaylist)
            .where(GroupPlaylist.owner_id == owner_id)
            .order_by(GroupPlaylist.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession,
        playlist_id: int,
        playlist_data: GroupPlaylistUpdate
    ) -> Optional[GroupPlaylist]:
        """Update group playlist details"""
        playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
        if not playlist:
            return None
        
        update_data = playlist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(playlist, field, value)
        
        await db.commit()
        await db.refresh(playlist)
        return playlist
    
    @staticmethod
    async def delete(db: AsyncSession, playlist_id: int) -> bool:
        """Delete group playlist (cascades to members, videos, invites)"""
        playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
        if not playlist:
            return False
        
        await db.delete(playlist)
        await db.commit()
        return True