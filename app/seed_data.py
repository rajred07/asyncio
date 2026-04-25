import asyncio
import sys
import os
import random
from datetime import datetime
from passlib.context import CryptContext

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL

from models.user import User
from models.playlist import Playlist
from models.video import Video
from constant import VALID_CATEGORIES, get_valid_scenarios, get_valid_vibes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 10 fake users
USERS_DATA = [
    {
        "username": f"testuser_{i}",
        "email": f"test{i}@example.com",
        "full_name": f"Test User {i}",
        "bio": f"I am test user {i} and I love watching playlists.",
        "preferred_categories": ["Gaming" if i % 2 == 0 else "Entertainment"],
    }
    for i in range(1, 11)
]

# Real YouTube video IDs pool
VIDEO_POOL = [
    {"id": "dQw4w9WgXcQ", "title": "Never Gonna Give You Up", "channel": "Rick Astley"},
    {"id": "jNQXAC9IVRw", "title": "Me at the zoo", "channel": "jawed"},
    {"id": "M7lc1UVf-VE", "title": "YouTube Rewind 2010", "channel": "YouTube"},
    {"id": "9bZkp7q19f0", "title": "Gangnam Style", "channel": "officialpsy"},
    {"id": "kJQP7kiw5Fk", "title": "Despacito", "channel": "Luis Fonsi"},
    {"id": "RgKAFK5djSk", "title": "See You Again", "channel": "Wiz Khalifa"},
    {"id": "JGwWNGJdvx8", "title": "Shape of You", "channel": "Ed Sheeran"},
    {"id": "ru0K8uYEZWw", "title": "Roar", "channel": "Katy Perry"},
]

async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Starting fake data generation...")
        
        # 1. Create 10 Users
        users = []
        for i, u_data in enumerate(USERS_DATA):
            user = User(
                username=u_data["username"],
                email=u_data["email"],
                full_name=u_data["full_name"],
                bio=u_data["bio"],
                profile_image=None,  # No profile image
                preferred_categories=u_data["preferred_categories"],
                hashed_password=pwd_context.hash("password123")
            )
            session.add(user)
            users.append(user)
        
        await session.flush()
        print("✅ 10 users created (password: password123)")
        
        # 2. Create 3 playlists for each user (30 total)
        total_playlists = 0
        total_videos = 0
        
        for user in users:
            for p_idx in range(1, 4):
                # We will make 1 out of every 5 playlists "featured" so Editor's Picks gets populated
                is_featured_flag = (total_playlists % 5 == 0)
                category = "Gaming" if p_idx % 2 == 0 else "Entertainment"
                
                playlist = Playlist(
                    title=f"{user.username}'s Playlist #{p_idx}",
                    description=f"A fantastic {category} collection.",
                    thumbnail=None,  # Use default frontend image
                    is_public=True,
                    owner_id=user.id,
                    category=category,
                    likes_count=random.randint(0, 100),
                    is_featured=is_featured_flag
                )
                session.add(playlist)
                await session.flush()
                total_playlists += 1
                
                # 3. Create 5-6 videos for each playlist
                num_videos = random.choice([5, 6])
                for v_idx in range(num_videos):
                    v_data = random.choice(VIDEO_POOL)
                    video = Video(
                        youtube_id=v_data["id"],
                        title=f"{v_data['title']} (Part {v_idx+1})",
                        channel_name=v_data["channel"],
                        thumbnail=None,  # No thumbnail, forces default fallback
                        views=random.randint(1000, 1000000),
                        duration=random.randint(180, 1200),
                        playlist_id=playlist.id,
                        added_by_id=user.id,
                        position=v_idx
                    )
                    session.add(video)
                    total_videos += 1
            
            # Flush after every user to avoid huge transactions
            await session.flush()
            # "Keep waiting time more" -> sleep slightly so the script clearly streams output
            await asyncio.sleep(0.5)

        await session.commit()
        print(f"✅ Created {total_playlists} playlists (None thumbnails, falling back to default)")
        print(f"✅ Created {total_videos} videos inside them")
        print("🎉 Seeding complete. You can test it out now.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
