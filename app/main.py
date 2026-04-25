from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables
from routes.user import router as user_router
from routes.playlist import router as playlist_router
from routes.group_playlist import router as group_playlist_router
from routes.search import router as search_router
from routes.watchlater import router as watchlater_router

# Import models in dependency order so SQLAlchemy registers relationships
from models.user import User
from models.playlist import Playlist
from models.video import Video
from models.playlist_like import PlaylistLike
from models.playlist_save import PlaylistSave
from models.playlist_view import PlaylistView
from models.group_playlist import GroupPlaylist
from models.group_member import GroupPlaylistMember
from models.group_video import GroupPlaylistVideo
from models.group_invite import GroupInvite


@asynccontextmanager
async def lifespan(app: FastAPI):
    # NOTE: drop_tables() is intentionally disabled for production.
    # Uncomment the line below ONLY for local dev DB reset:
    # await drop_tables()
    await create_tables()
    yield


app = FastAPI(
    title="PlaylistGenius API",
    description="Async API for saving and managing YouTube playlists (Normal & Group)",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(playlist_router)
app.include_router(group_playlist_router)
app.include_router(search_router)
app.include_router(watchlater_router)


@app.get("/")
async def root():
    return {
        "message": "PlaylistGenius API",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Normal Playlists with Tag System",
            "Group Playlists",
            "User Management",
            "Social Feed & Discovery",
        ],
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api")
async def api_info():
    return {
        "version": "2.0.0",
        "endpoints": {
            "users": "/api/users",
            "playlists": "/api/playlists",
            "group_playlists": "/api/group-playlists",
            "playlist_tags": "/api/playlists/tag-options",
            "search": "/api/search",
            "watch_later": "/api/watchlater",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)