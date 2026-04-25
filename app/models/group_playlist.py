from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class GroupPlaylist(Base):
    __tablename__ = "group_playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    
    # Owner (creator of the group playlist)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("GroupPlaylistMember", back_populates="group_playlist", cascade="all, delete-orphan")
    videos = relationship("GroupPlaylistVideo", back_populates="group_playlist", cascade="all, delete-orphan")
    invites = relationship("GroupInvite", back_populates="group_playlist", cascade="all, delete-orphan")
    
    @property
    def video_count(self):
        try:
            return len(self.videos) if hasattr(self, '_sa_instance_state') and self.videos else 0
        except:
            return 0
    
    @property
    def member_count(self):
        try:
            return len(self.members) if hasattr(self, '_sa_instance_state') and self.members else 0
        except:
            return 0