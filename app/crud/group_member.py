from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from models.group_member import GroupPlaylistMember, MemberRole
from models.user import User
from typing import Optional, List

class GroupMemberCRUD:
    
    @staticmethod
    async def get_member(
        db: AsyncSession,
        playlist_id: int,
        user_id: int
    ) -> Optional[GroupPlaylistMember]:
        """Get a specific member from a group playlist"""
        result = await db.execute(
            select(GroupPlaylistMember)
            .options(selectinload(GroupPlaylistMember.user))
            .where(
                and_(
                    GroupPlaylistMember.group_playlist_id == playlist_id,
                    GroupPlaylistMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_members(
        db: AsyncSession,
        playlist_id: int
    ) -> List[GroupPlaylistMember]:
        """Get all members of a group playlist"""
        result = await db.execute(
            select(GroupPlaylistMember)
            .options(selectinload(GroupPlaylistMember.user))
            .where(GroupPlaylistMember.group_playlist_id == playlist_id)
            .order_by(GroupPlaylistMember.joined_at.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def add_member(
        db: AsyncSession,
        playlist_id: int,
        user_id: int,
        role: MemberRole = MemberRole.MEMBER
    ) -> GroupPlaylistMember:
        """Add a new member to group playlist"""
        # Check if already a member
        existing = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
        if existing:
            return existing
        
        new_member = GroupPlaylistMember(
            group_playlist_id=playlist_id,
            user_id=user_id,
            role=role
        )
        
        db.add(new_member)
        await db.commit()
        await db.refresh(new_member)
        return new_member
    
    @staticmethod
    async def update_role(
        db: AsyncSession,
        playlist_id: int,
        user_id: int,
        new_role: MemberRole
    ) -> Optional[GroupPlaylistMember]:
        """Update a member's role"""
        member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
        if not member:
            return None
        
        member.role = new_role
        await db.commit()
        await db.refresh(member)
        return member
    
    @staticmethod
    async def remove_member(
        db: AsyncSession,
        playlist_id: int,
        user_id: int
    ) -> bool:
        """Remove a member from group playlist"""
        member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
        if not member:
            return False
        
        await db.delete(member)
        await db.commit()
        return True
    
    @staticmethod
    async def is_member(
        db: AsyncSession,
        playlist_id: int,
        user_id: int
    ) -> bool:
        """Check if user is a member of the group playlist"""
        member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
        return member is not None
    
    @staticmethod
    async def get_member_role(
        db: AsyncSession,
        playlist_id: int,
        user_id: int
    ) -> Optional[MemberRole]:
        """Get the role of a member in a group playlist"""
        member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
        return member.role if member else None