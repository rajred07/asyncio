# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, and_
# from sqlalchemy.orm import selectinload
# from models.group_invite import GroupInvite, InviteStatus
# from typing import Optional, List
# from datetime import datetime, timedelta
# import secrets

# class GroupInviteCRUD:
    
#     @staticmethod
#     def generate_invite_token() -> str:
#         """Generate a unique invite token"""
#         return secrets.token_urlsafe(32)
    
#     @staticmethod
#     async def create(
#         db: AsyncSession,
#         playlist_id: int,
#         inviter_id: int,
#         invitee_id: int,
#         expires_in_days: int = 7
#     ) -> Optional[GroupInvite]:
#         """Create a new invite"""
#         # Check if invite already exists
#         existing = await GroupInviteCRUD.get_pending_invite(
#             db, playlist_id, invitee_id
#         )
#         if existing:
#             return existing  # Return existing pending invite
        
#         # Create new invite
#         new_invite = GroupInvite(
#             group_playlist_id=playlist_id,
#             inviter_id=inviter_id,
#             invitee_id=invitee_id,
#             status=InviteStatus.PENDING,
#             invite_token=GroupInviteCRUD.generate_invite_token(),
#             expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
#         )
        
#         db.add(new_invite)
#         await db.commit()
#         await db.refresh(new_invite)
#         return new_invite
    
#     @staticmethod
#     async def get_by_id(
#         db: AsyncSession,
#         invite_id: int
#     ) -> Optional[GroupInvite]:
#         """Get invite by ID with relationships loaded"""
#         result = await db.execute(
#             select(GroupInvite)
#             .options(
#                 selectinload(GroupInvite.group_playlist),
#                 selectinload(GroupInvite.inviter),
#                 selectinload(GroupInvite.invitee)
#             )
#             .where(GroupInvite.id == invite_id)
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_pending_invite(
#         db: AsyncSession,
#         playlist_id: int,
#         invitee_id: int
#     ) -> Optional[GroupInvite]:
#         """Check if user already has a pending invite for this playlist"""
#         result = await db.execute(
#             select(GroupInvite)
#             .where(
#                 and_(
#                     GroupInvite.group_playlist_id == playlist_id,
#                     GroupInvite.invitee_id == invitee_id,
#                     GroupInvite.status == InviteStatus.PENDING
#                 )
#             )
#         )
#         return result.scalar_one_or_none()
    
#     @staticmethod
#     async def get_user_pending_invites(
#         db: AsyncSession,
#         user_id: int
#     ) -> List[GroupInvite]:
#         """Get all pending invites for a user"""
#         result = await db.execute(
#             select(GroupInvite)
#             .options(
#                 selectinload(GroupInvite.group_playlist),
#                 selectinload(GroupInvite.inviter)
#             )
#             .where(
#                 and_(
#                     GroupInvite.invitee_id == user_id,
#                     GroupInvite.status == InviteStatus.PENDING
#                 )
#             )
#             .order_by(GroupInvite.created_at.desc())
#         )
#         return result.scalars().all()
    
#     @staticmethod
#     async def accept_invite(
#         db: AsyncSession,
#         invite_id: int
#     ) -> Optional[GroupInvite]:
#         """Accept an invite"""
#         invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#         if not invite or invite.status != InviteStatus.PENDING:
#             return None
        
#         if invite.is_expired:
#             invite.status = InviteStatus.EXPIRED
#             await db.commit()
#             return None
        
#         invite.status = InviteStatus.ACCEPTED
#         invite.responded_at = datetime.utcnow()
        
#         await db.commit()
#         await db.refresh(invite)
#         return invite
    
#     @staticmethod
#     async def reject_invite(
#         db: AsyncSession,
#         invite_id: int
#     ) -> Optional[GroupInvite]:
#         """Reject an invite"""
#         invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#         if not invite or invite.status != InviteStatus.PENDING:
#             return None
        
#         invite.status = InviteStatus.REJECTED
#         invite.responded_at = datetime.utcnow()
        
#         await db.commit()
#         await db.refresh(invite)
#         return invite
    
#     @staticmethod
#     async def delete(db: AsyncSession, invite_id: int) -> bool:
#         """Delete an invite"""
#         invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#         if not invite:
#             return False
        
#         await db.delete(invite)
#         await db.commit()
#         return True



from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from models.group_invite import GroupInvite, InviteStatus
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import secrets

class GroupInviteCRUD:
    
    @staticmethod
    def generate_invite_token() -> str:
        """Generate a unique invite token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def create(
        db: AsyncSession,
        playlist_id: int,
        inviter_id: int,
        invitee_id: int,
        expires_in_days: int = 7
    ) -> Optional[GroupInvite]:
        """Create a new invite"""
        # Check if invite already exists
        existing = await GroupInviteCRUD.get_pending_invite(
            db, playlist_id, invitee_id
        )
        if existing:
            return existing  # Return existing pending invite
        
        # Create new invite
        new_invite = GroupInvite(
            group_playlist_id=playlist_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            status=InviteStatus.PENDING,
            invite_token=GroupInviteCRUD.generate_invite_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        )
        
        db.add(new_invite)
        await db.commit()
        await db.refresh(new_invite)
        return new_invite
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        invite_id: int
    ) -> Optional[GroupInvite]:
        """Get invite by ID with relationships loaded"""
        result = await db.execute(
            select(GroupInvite)
            .options(
                selectinload(GroupInvite.group_playlist),
                selectinload(GroupInvite.inviter),
                selectinload(GroupInvite.invitee)
            )
            .where(GroupInvite.id == invite_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_pending_invite(
        db: AsyncSession,
        playlist_id: int,
        invitee_id: int
    ) -> Optional[GroupInvite]:
        """Check if user already has a pending invite for this playlist"""
        result = await db.execute(
            select(GroupInvite)
            .where(
                and_(
                    GroupInvite.group_playlist_id == playlist_id,
                    GroupInvite.invitee_id == invitee_id,
                    GroupInvite.status == InviteStatus.PENDING
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_pending_invites(
        db: AsyncSession,
        user_id: int
    ) -> List[GroupInvite]:
        """Get all pending invites for a user"""
        result = await db.execute(
            select(GroupInvite)
            .options(
                selectinload(GroupInvite.group_playlist),
                selectinload(GroupInvite.inviter)
            )
            .where(
                and_(
                    GroupInvite.invitee_id == user_id,
                    GroupInvite.status == InviteStatus.PENDING
                )
            )
            .order_by(GroupInvite.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def accept_invite(
        db: AsyncSession,
        invite_id: int
    ) -> Optional[GroupInvite]:
        """Accept an invite"""
        invite = await GroupInviteCRUD.get_by_id(db, invite_id)
        if not invite or invite.status != InviteStatus.PENDING:
            return None
        
        if invite.is_expired:
            invite.status = InviteStatus.EXPIRED
            await db.commit()
            return None
        
        invite.status = InviteStatus.ACCEPTED
        invite.responded_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(invite)
        return invite
    
    @staticmethod
    async def reject_invite(
        db: AsyncSession,
        invite_id: int
    ) -> Optional[GroupInvite]:
        """Reject an invite"""
        invite = await GroupInviteCRUD.get_by_id(db, invite_id)
        if not invite or invite.status != InviteStatus.PENDING:
            return None
        
        invite.status = InviteStatus.REJECTED
        invite.responded_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(invite)
        return invite
    
    @staticmethod
    async def delete(db: AsyncSession, invite_id: int) -> bool:
        """Delete an invite"""
        invite = await GroupInviteCRUD.get_by_id(db, invite_id)
        if not invite:
            return False
        
        await db.delete(invite)
        await db.commit()
        return True