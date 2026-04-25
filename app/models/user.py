from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, JSON, select, func
from sqlalchemy.orm import relationship, column_property
from database import Base


# Association table — followers (many-to-many self-referential)
followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id",  Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    email           = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name       = Column(String(100), nullable=True)
    bio             = Column(String(500), nullable=True)
    profile_image   = Column(String(255), nullable=True)

    # Preferred content categories for personalised feed (e.g. ["Gaming", "Education"])
    preferred_categories = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owned_playlists = relationship(
        "Playlist",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # lazy="noload" — we query counts directly via column_property below
    following = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.following_id,
        backref="followers",
        lazy="noload",
    )


# column_property subqueries — added after class definition so the table exists
User.followers_count = column_property(
    select(func.count(followers_table.c.follower_id))
    .where(followers_table.c.following_id == User.id)
    .correlate_except(followers_table)
    .scalar_subquery()
)

User.following_count = column_property(
    select(func.count(followers_table.c.following_id))
    .where(followers_table.c.follower_id == User.id)
    .correlate_except(followers_table)
    .scalar_subquery()
)