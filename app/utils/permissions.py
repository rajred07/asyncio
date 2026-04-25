from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.playlist import Playlist, PlaylistType, playlist_members, MemberRole
from models.video import Video
from models.user import User
from typing import Optional

async def get_member_role(db: AsyncSession, user_id: int, playlist_id: int) -> Optional[str]:
    """Get user's role in a playlist (admin/member/None)"""
    result = await db.execute(
        select(playlist_members.c.role)
        .where(
            and_(
                playlist_members.c.user_id == user_id,
                playlist_members.c.playlist_id == playlist_id
            )
        )
    )
    role = result.scalar_one_or_none()
    return role

async def is_owner(user: User, playlist: Playlist) -> bool:
    """Check if user is the playlist owner"""
    return user.id == playlist.owner_id

async def is_admin(db: AsyncSession, user: User, playlist: Playlist) -> bool:
    """Check if user is admin (owner is automatically admin)"""
    if await is_owner(user, playlist):
        return True
    
    role = await get_member_role(db, user.id, playlist.id)
    return role == MemberRole.ADMIN

async def is_member(db: AsyncSession, user: User, playlist: Playlist) -> bool:
    """Check if user is a member (admin and owner count as members)"""
    if await is_owner(user, playlist):
        return True
    
    role = await get_member_role(db, user.id, playlist.id)
    return role is not None

async def can_view_playlist(db: AsyncSession, user: User, playlist: Playlist) -> bool:
    """Check if user can view playlist"""
    # Normal public playlists - anyone can view
    if playlist.playlist_type == PlaylistType.NORMAL and playlist.is_public:
        return True
    
    # Community playlists - anyone can view
    if playlist.playlist_type == PlaylistType.COMMUNITY:
        return True
    
    # Owner can always view
    if await is_owner(user, playlist):
        return True
    
    # Group/Private playlists - only members
    if playlist.playlist_type == PlaylistType.GROUP or not playlist.is_public:
        return await is_member(db, user, playlist)
    
    return False

async def can_add_video(db: AsyncSession, user: User, playlist: Playlist) -> bool:
    """Check if user can add videos"""
    # Normal playlists - only owner
    if playlist.playlist_type == PlaylistType.NORMAL:
        return await is_owner(user, playlist)
    
    # Group/Community - any member can add
    return await is_member(db, user, playlist)

async def can_delete_video(db: AsyncSession, user: User, playlist: Playlist, video: Video) -> bool:
    """Check if user can delete a video"""
    # Normal playlists - only owner
    if playlist.playlist_type == PlaylistType.NORMAL:
        return await is_owner(user, playlist)
    
    # Owner can delete anything
    if await is_owner(user, playlist):
        return True
    
    # Admins can delete anything
    if await is_admin(db, user, playlist):
        return True
    
    # Members can only delete their own videos
    if await is_member(db, user, playlist):
        return video.added_by_id == user.id
    
    return False

async def can_manage_members(db: AsyncSession, user: User, playlist: Playlist) -> bool:
    """Check if user can add/remove members"""
    # Normal playlists don't have members
    if playlist.playlist_type == PlaylistType.NORMAL:
        return False
    
    # Only owner and admins can manage members
    return await is_admin(db, user, playlist)

async def can_promote_to_admin(user: User, playlist: Playlist) -> bool:
    """Check if user can promote others to admin (owner only)"""
    return await is_owner(user, playlist)