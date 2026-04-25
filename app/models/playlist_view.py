from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class PlaylistView(Base):
    __tablename__ = "playlist_views"
    
    id          = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False, index=True)
    viewer_ip   = Column(String(45), nullable=False)   # 45 chars covers IPv6
    viewed_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
