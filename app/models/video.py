from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # YouTube video data
    youtube_id = Column(String(50), nullable=False, index=True)  # YouTube video ID
    title = Column(String(300), nullable=False)
    channel_name = Column(String(200), nullable=False)
    thumbnail = Column(String(500), nullable=True)
    views = Column(BigInteger, default=0)  # YouTube views
    duration = Column(Integer, default=0)   # Duration in seconds (from YouTube API)
    youtube_description = Column(Text, nullable=True)  # Original YouTube description
    
    # User's custom description for this video
    user_description = Column(Text, nullable=True)
    
    # Playlist relationship
    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False)
    
    # Who added this video
    added_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Position in playlist (for ordering)
    position = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    playlist = relationship("Playlist", back_populates="videos")
    added_by = relationship("User", foreign_keys=[added_by_id])