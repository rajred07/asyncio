from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class GroupPlaylistMember(Base):
    __tablename__ = "group_playlist_members"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Which group playlist
    group_playlist_id = Column(Integer, ForeignKey('group_playlists.id', ondelete='CASCADE'), nullable=False)
    
    # Which user
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Role in this group playlist
    role = Column(Enum(MemberRole), nullable=False, default=MemberRole.MEMBER)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group_playlist = relationship("GroupPlaylist", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])