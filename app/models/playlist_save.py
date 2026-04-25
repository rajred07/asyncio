from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class PlaylistSave(Base):
    __tablename__ = "playlist_saves"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="saved_playlists")
    playlist = relationship("Playlist", back_populates="saves")
    
    # Prevent duplicate saves from same user
    __table_args__ = (
        UniqueConstraint('user_id', 'playlist_id', name='unique_user_playlist_save'),
    )