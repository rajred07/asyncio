"""
EaTube Watch Later Background Worker
=====================================
Imports and calls functions directly from preprocespart1.py to run the
full pipeline: YouTube API enrichment → Gemini categorization → DB insert.

Supports chunked processing for large Watch Later lists (300+ videos):
  - Chunk 1: videos 0–99
  - Chunk 2: videos 100–199
  - Chunk 3: videos 200–309
Each chunk saves immediately to DB so partial results survive crashes.
"""

import uuid
import asyncio
import sys
import os
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sa_delete

# ─── Import pipeline functions (now co-located in app/utils/) ─────────────
from utils.preprocespart1 import (
    fetch_youtube_metadata,
    compute_features,
    categorize_with_gemini,
    validate_categorizations,
    generate_playlists,
)
from utils.config import (
    YOUTUBE_API_KEY,
    GEMINI_API_KEY,
    YOUTUBE_API_BATCH_SIZE,
    GEMINI_BATCH_SIZE,
)

from models.playlist import Playlist
from models.video import Video
from database import async_session_maker
from utils.url_utils import (
    clean_youtube_url,
    get_thumbnail_url,
    parse_duration_string,
    parse_formatted_duration_to_seconds,
)

# ─── In-memory job store ─────────────────────────────────────────────────────
# For production, move this to a DB table or Redis.
jobs: dict[str, dict] = {}

CHUNK_SIZE = 100  # Process 100 videos per chunk


def create_job(user_id: int) -> str:
    """Create a new job entry and return the job_id."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "user_id": user_id,
        "status": "queued",
        "progress": "Job queued, waiting to start...",
        "playlists_created": 0,
        "videos_imported": 0,
        "total_videos": 0,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    return job_id


def _update_job(job_id: str, **kwargs):
    """Helper to update job fields."""
    if job_id in jobs:
        jobs[job_id].update(kwargs)


# ─── Main Background Task ─────────────────────────────────────────────────────

async def run_watchlater_pipeline(
    job_id: str,
    raw_json: dict,
    user_id: int,
):
    """
    Full Watch Later pipeline. Runs as a background asyncio task.
    
    Steps:
      1. Parse videos from uploaded JSON
      2. Process in chunks of 100:
           a. YouTube API enrichment
           b. Gemini AI categorization
           c. Validation
      3. Generate playlists from all enriched videos
      4. Save playlists + videos to DB
    """
    try:
        _update_job(job_id, status="processing", progress="Starting pipeline...")

        # ── Step 0: Parse videos from uploaded JSON ──
        videos_raw = raw_json.get("videos", [])
        scraped_at = raw_json.get("scrapedAt", datetime.now(timezone.utc).isoformat())
        total = len(videos_raw)

        if total == 0:
            _update_job(job_id, status="failed", error="No videos found in uploaded file.")
            return

        _update_job(job_id, total_videos=total,
                    progress=f"Found {total} videos. Starting enrichment...")

        # ── Step 1: Delete existing watch later playlists for this user ──
        # (Fresh import — wipe old ones cleanly)
        async with async_session_maker() as db:
            await _delete_existing_watchlater(db, user_id)

        # ── Step 2: Process in chunks ──
        all_enriched = []
        chunks = [videos_raw[i:i + CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]

        for chunk_idx, chunk_videos in enumerate(chunks):
            chunk_num = chunk_idx + 1
            chunk_start = chunk_idx * CHUNK_SIZE
            chunk_end = chunk_start + len(chunk_videos)

            _update_job(
                job_id,
                progress=f"Chunk {chunk_num}/{len(chunks)}: "
                         f"Enriching videos {chunk_start+1}–{chunk_end} via YouTube API..."
            )

            # Run blocking pipeline functions in a thread pool
            # (they use requests/google-genai which are sync)
            enriched_chunk = await asyncio.get_event_loop().run_in_executor(
                None,
                _process_chunk,
                chunk_videos,
                scraped_at,
                job_id,
                chunk_num,
                len(chunks),
            )

            all_enriched.extend(enriched_chunk)
            _update_job(
                job_id,
                videos_imported=len(all_enriched),
                progress=f"Chunk {chunk_num}/{len(chunks)} complete. "
                         f"{len(all_enriched)}/{total} videos enriched."
            )

        # ── Step 3: Generate playlists ──
        _update_job(job_id, progress="Generating smart playlists...")

        playlists_data = await asyncio.get_event_loop().run_in_executor(
            None, generate_playlists, all_enriched
        )

        # ── Step 4: Save to DB ──
        _update_job(job_id, progress="Saving playlists to database...")

        async with async_session_maker() as db:
            playlists_created = await _save_to_db(
                db, playlists_data, all_enriched, user_id
            )

        _update_job(
            job_id,
            status="completed",
            progress=f"Done! Created {playlists_created} playlists with {len(all_enriched)} videos.",
            playlists_created=playlists_created,
            videos_imported=len(all_enriched),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        _update_job(
            job_id,
            status="failed",
            error=str(e),
            progress=f"Pipeline failed: {str(e)}",
        )


# ─── Sync chunk processor (runs in thread pool) ───────────────────────────────

def _process_chunk(
    chunk_videos: list,
    scraped_at: str,
    job_id: str,
    chunk_num: int,
    total_chunks: int,
) -> list:
    """
    Synchronous pipeline for one chunk of videos.
    Runs in executor to avoid blocking the async event loop.
    """
    # Layer 1: YouTube API enrichment
    video_ids = [v["videoId"] for v in chunk_videos]
    youtube_data = fetch_youtube_metadata(video_ids, YOUTUBE_API_KEY)

    # Layer 2: Feature engineering
    enriched = compute_features(chunk_videos, youtube_data, scraped_at)

    # Layer 3: Gemini categorization
    enriched = categorize_with_gemini(enriched, GEMINI_API_KEY)

    # Layer 4: Validation
    enriched = validate_categorizations(enriched)

    return enriched


# ─── DB Save Logic ────────────────────────────────────────────────────────────

async def _delete_existing_watchlater(db: AsyncSession, user_id: int):
    """Delete all existing watchlater playlists for this user (fresh import)."""
    result = await db.execute(
        select(Playlist).where(
            Playlist.owner_id == user_id,
            Playlist.scenario == "watchlater"
        )
    )
    existing = result.scalars().all()
    for pl in existing:
        await db.delete(pl)
    await db.commit()


async def _save_to_db(
    db: AsyncSession,
    playlists_data: dict,
    all_enriched: list,
    user_id: int,
) -> int:
    """
    Insert all playlists + videos into DB.
    Returns count of playlists created.
    """
    # Build lookup: videoId → enriched video data (for thumbnails/views)
    enriched_lookup = {v["videoId"]: v for v in all_enriched}

    playlists_created = 0

    for pl in playlists_data.get("playlists", []):
        pl_videos = pl.get("videos", [])
        if not pl_videos:
            continue

        # ── Determine playlist metadata ──
        is_category_playlist = pl.get("type") == "category"

        # Thumbnail: use first video's YouTube thumbnail
        first_video_id = pl_videos[0].get("videoId", "")
        thumbnail = get_thumbnail_url(first_video_id)

        # Total duration
        total_duration_secs = pl.get("totalDurationSeconds", 0)
        if not total_duration_secs:
            total_duration_secs = parse_formatted_duration_to_seconds(
                pl.get("totalDurationFormatted", "0:00")
            )

        # Vibes: only category playlists have dominantMood
        vibes = []
        if is_category_playlist and pl.get("dominantMood"):
            vibes = [pl["dominantMood"]]

        # Hook description: truncate to 140 chars
        raw_desc = pl.get("description", "")
        hook = raw_desc[:140] if raw_desc else None

        # ── Create Playlist row ──
        db_playlist = Playlist(
            title=pl["title"],
            description=raw_desc,
            thumbnail=thumbnail,
            is_public=False,                # Watch Later is personal/private
            owner_id=user_id,
            scenario="watchlater",
            category="Watch Later",
            vibes=vibes,
            hook_description=hook,
            video_count=pl.get("videoCount", len(pl_videos)),
            total_duration=total_duration_secs,
        )
        db.add(db_playlist)
        await db.flush()  # Get the playlist ID without committing

        # ── Create Video rows ──
        for vid in pl_videos:
            video_id = vid.get("videoId", "")

            # Smart playlists have "duration" string; category playlists have "durationSeconds"
            duration_secs = vid.get("durationSeconds", 0)
            if not duration_secs:
                duration_secs = parse_duration_string(vid.get("duration", "0:00"))

            # Get extra data from enriched lookup if available
            enriched_v = enriched_lookup.get(video_id, {})
            view_count = (
                vid.get("viewCount", 0)
                or enriched_v.get("engagement", {}).get("viewCount", 0)
            )

            # Summary: category playlists have it, smart playlists don't
            summary = vid.get("summary", "") or ""

            db_video = Video(
                youtube_id=video_id,
                title=vid.get("title", ""),
                channel_name=(
                    vid.get("channelName", "")
                    or enriched_v.get("basic", {}).get("channelName", "")
                    or ""
                ),
                thumbnail=get_thumbnail_url(video_id),
                views=view_count,
                duration=duration_secs,
                youtube_description=summary,
                user_description=None,
                playlist_id=db_playlist.id,
                added_by_id=user_id,
                position=vid.get("position", 0),
            )
            db.add(db_video)

        playlists_created += 1

    await db.commit()
    return playlists_created
