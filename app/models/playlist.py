from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail   = Column(String(500), nullable=True)

    # Visibility
    is_public = Column(Boolean, default=True)

    # Owner (creator of the playlist)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # ── Tag System Fields (all optional) ──────────────────────────────────
    # Step 1: The Big Split — main category
    category = Column(String(50), nullable=True)   # "Gaming" | "Entertainment" | "Education" | "Music"

    # Step 2: The Scenario — when to watch
    scenario = Column(String(50), nullable=True)   # e.g. "Meal Time", "High Focus", "Workout"

    # Step 3: The Vibes — sub-genres (max 2)
    vibes = Column(JSON, nullable=True)            # e.g. ["Competitive", "Tutorial/Guide"]

    # Step 4: The Hook — why this playlist is worth saving (max 140 chars)
    hook_description = Column(String(140), nullable=True)
    # ──────────────────────────────────────────────────────────────────────

    # ── Cached Counter Fields ──────────────────────────────────────────────
    likes_count    = Column(Integer, default=0, nullable=False)
    saves_count    = Column(Integer, default=0, nullable=False)
    views_count    = Column(Integer, default=0, nullable=False)
    video_count    = Column(Integer, default=0, nullable=False)
    total_duration = Column(Integer, default=0, nullable=False)  # sum of video durations (seconds)
    # ──────────────────────────────────────────────────────────────────────

    # ── Editorial Flags ───────────────────────────────────────────────────
    is_featured = Column(Boolean, default=False, nullable=False)  # admin-curated Editor's Picks
    # ──────────────────────────────────────────────────────────────────────

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner  = relationship("User", back_populates="owned_playlists")
    videos = relationship("Video", back_populates="playlist", cascade="all, delete-orphan")
    likes  = relationship("PlaylistLike", back_populates="playlist", cascade="all, delete-orphan")
    saves  = relationship("PlaylistSave", back_populates="playlist", cascade="all, delete-orphan")

    @property
    def owner_username(self):
        try:
            return self.owner.username if self.owner else None
        except Exception:
            return None