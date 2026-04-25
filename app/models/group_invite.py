from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime, timedelta, timezone

class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class GroupInvite(Base):
    __tablename__ = "group_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Which group playlist
    group_playlist_id = Column(Integer, ForeignKey('group_playlists.id', ondelete='CASCADE'), nullable=False)
    
    # Who sent the invite
    inviter_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Who is being invited
    invitee_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Invite status
    status = Column(Enum(InviteStatus), nullable=False, default=InviteStatus.PENDING)
    
    # Optional: Unique token for invite links
    invite_token = Column(String(100), unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    group_playlist = relationship("GroupPlaylist", back_populates="invites")
    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee = relationship("User", foreign_keys=[invitee_id])
    
    @property
    def is_expired(self):
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return True
        return False