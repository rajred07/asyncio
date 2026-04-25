from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class PlaylistLike(Base):
    __tablename__ = "playlist_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="liked_playlists")
    playlist = relationship("Playlist", back_populates="likes")
    
    # Prevent duplicate likes from same user
    __table_args__ = (
        UniqueConstraint('user_id', 'playlist_id', name='unique_user_playlist_like'),
    )