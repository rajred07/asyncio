from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class GroupPlaylistVideo(Base):
    __tablename__ = "group_playlist_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Which group playlist this video belongs to
    group_playlist_id = Column(Integer, ForeignKey('group_playlists.id', ondelete='CASCADE'), nullable=False)
    
    # YouTube video data
    youtube_id = Column(String(50), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    channel_name = Column(String(200), nullable=False)
    thumbnail = Column(String(500), nullable=True)
    views = Column(BigInteger, default=0)
    youtube_description = Column(Text, nullable=True)
    
    # User's custom description
    user_description = Column(Text, nullable=True)
    
    # Who added this video
    added_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Position in playlist (for ordering)
    position = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    group_playlist = relationship("GroupPlaylist", back_populates="videos")
    added_by = relationship("User", foreign_keys=[added_by_id])