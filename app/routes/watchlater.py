"""
Watch Later Import Routes
==========================
POST /api/watchlater/import         → Upload watchlater.json file, start background pipeline
POST /api/watchlater/import-direct  → Chrome Extension calls this with raw JSON + JWT token
GET  /api/watchlater/status/{job_id} → Poll processing progress
GET  /api/watchlater/playlists       → Fetch all imported watchlater playlists for user
DELETE /api/watchlater/clear         → Delete all watchlater playlists for user
"""
import asyncio
import json
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from models.playlist import Playlist
from utils.auth import get_current_active_user
from utils.watchlater_worker import (
    create_job,
    run_watchlater_pipeline,
    jobs,
    _delete_existing_watchlater,
)

router = APIRouter(prefix="/api/watchlater", tags=["Watch Later"])


# ─── POST /api/watchlater/import ─────────────────────────────────────────────

@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def import_watchlater(
    file: UploadFile = File(..., description="watchlater.json from Chrome Extension"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload your watchlater.json from the Chrome Extension.
    Returns a job_id immediately. Poll /status/{job_id} to track progress.
    
    The pipeline runs in the background:
      - YouTube API enrichment (in chunks of 100)
      - Gemini AI categorization (10 per batch)
      - Saves smart playlists to your account
    """
    # Validate file type
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are accepted. Upload your watchlater.json file."
        )

    # Read and parse JSON
    try:
        content = await file.read()
        raw_json = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON file: {str(e)}"
        )

    # Validate structure
    if "videos" not in raw_json:
        raise HTTPException(
            status_code=400,
            detail="Invalid format: file must contain a 'videos' array. "
                   "Make sure to use the TubeSort Chrome Extension to generate this file."
        )

    video_count = len(raw_json.get("videos", []))
    if video_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No videos found in the file."
        )

    # Create job and fire background task
    job_id = create_job(current_user.id)

    asyncio.create_task(
        run_watchlater_pipeline(
            job_id=job_id,
            raw_json=raw_json,
            user_id=current_user.id,
        )
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "total_videos": video_count,
        "message": f"Processing started for {video_count} videos. "
                   f"Poll /api/watchlater/status/{job_id} to track progress.",
        "status_url": f"/api/watchlater/status/{job_id}",
    }


# ─── POST /api/watchlater/import-direct (Chrome Extension) ───────────────────

class WatchLaterVideoItem(BaseModel):
    videoId: str
    url: str | None = None
    title: str | None = None
    savedIndex: int | None = None

class WatchLaterDirectPayload(BaseModel):
    videos: List[WatchLaterVideoItem]
    scrapedAt: str | None = None


@router.post("/import-direct", status_code=status.HTTP_202_ACCEPTED)
async def import_watchlater_direct(
    payload: WatchLaterDirectPayload,
    current_user: User = Depends(get_current_active_user),
):
    """
    Called directly by the Chrome Extension with the scraped video list.
    The extension sends:
      {
        "videos": [{"videoId": "abc123", "url": "...", "title": "...", "savedIndex": 0}, ...],
        "scrapedAt": "2026-02-28T12:00:00Z"
      }
    
    The backend handles all YouTube API calls + Gemini categorization in the background.
    Returns job_id immediately for polling.
    """
    videos = [v.model_dump() for v in payload.videos]

    if not videos:
        raise HTTPException(status_code=400, detail="No videos provided.")

    # Build the same shape as watchlater.json for the pipeline
    raw_json = {
        "videos": videos,
        "scrapedAt": payload.scrapedAt or "",
        "totalVideos": len(videos),
    }

    video_count = len(videos)
    job_id = create_job(current_user.id)

    asyncio.create_task(
        run_watchlater_pipeline(
            job_id=job_id,
            raw_json=raw_json,
            user_id=current_user.id,
        )
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "total_videos": video_count,
        "message": f"Received {video_count} videos. Processing in background...",
        "status_url": f"/api/watchlater/status/{job_id}",
    }



@router.get("/status/{job_id}")
async def get_import_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Poll this endpoint every 3-5 seconds to track import progress.
    
    Statuses:
      - queued     → Job waiting to start
      - processing → Pipeline running
      - completed  → Done, playlists are saved
      - failed     → Something went wrong (check 'error' field)
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="Job not found. It may have expired or never existed."
        )

    job = jobs[job_id]

    # Security: only let the owner check their own job
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "total_videos": job["total_videos"],
        "videos_imported": job["videos_imported"],
        "playlists_created": job["playlists_created"],
        "error": job["error"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
    }


# ─── GET /api/watchlater/playlists ───────────────────────────────────────────

@router.get("/playlists")
async def get_watchlater_playlists(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all Watch Later imported playlists for the current user.
    Use this after import completes to display the playlists.
    """
    result = await db.execute(
        select(Playlist).where(
            Playlist.owner_id == current_user.id,
            Playlist.scenario == "watchlater"
        ).order_by(Playlist.video_count.desc())
    )
    playlists = result.scalars().all()

    return {
        "count": len(playlists),
        "playlists": [
            {
                "id": pl.id,
                "title": pl.title,
                "thumbnail": pl.thumbnail,
                "video_count": pl.video_count,
                "total_duration": pl.total_duration,
                "vibes": pl.vibes,
                "hook_description": pl.hook_description,
                "scenario": pl.scenario,
                "created_at": pl.created_at,
            }
            for pl in playlists
        ]
    }


# ─── DELETE /api/watchlater/clear ────────────────────────────────────────────

@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_watchlater_playlists(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all Watch Later imported playlists for the current user.
    Use this before re-importing to start fresh.
    """
    await _delete_existing_watchlater(db, current_user.id)
    return {"message": "All Watch Later playlists deleted successfully."}
