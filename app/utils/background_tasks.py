from sqlalchemy.ext.asyncio import AsyncSession
from utils.youtube import get_playlist_video_ids, get_videos_metadata_batch
from crud.group_video import GroupVideoCRUD
from schemas.group_video import GroupVideoCreate
from utils.cache import generate_cache_key, set_cached_data, get_cached_data
import json

async def import_playlist_task(
    db: AsyncSession,
    task_id: str,
    playlist_id: int,
    youtube_playlist_url: str,
    added_by_id: int,
    max_videos: int = 50
):
    """
    Background task to import YouTube playlist videos into group playlist
    
    Stores progress in Redis for real-time tracking
    """
    try:
        # Initialize progress
        progress = {
            "task_id": task_id,
            "status": "processing",
            "total_videos": 0,
            "imported": 0,
            "failed": 0,
            "skipped_duplicates": 0,
            "progress_percentage": 0,
            "current_video": None,
            "error": None
        }
        
        # Store initial progress
        cache_key = generate_cache_key("import_task", task_id)
        set_cached_data(cache_key, progress, ttl=3600)  # 1 hour
        
        # Step 1: Get playlist video IDs
        print(f"📋 Task {task_id}: Fetching playlist video IDs...")
        playlist_data = await get_playlist_video_ids(youtube_playlist_url, max_results=max_videos)
        video_ids = playlist_data["video_ids"]
        
        progress["total_videos"] = len(video_ids)
        set_cached_data(cache_key, progress, ttl=3600)
        
        if not video_ids:
            progress["status"] = "completed"
            progress["error"] = "No videos found in playlist"
            set_cached_data(cache_key, progress, ttl=3600)
            return
        
        print(f"📋 Task {task_id}: Found {len(video_ids)} videos")
        
        # Step 2: Fetch metadata in batches
        print(f"🔍 Task {task_id}: Fetching video metadata...")
        videos_metadata = await get_videos_metadata_batch(video_ids)
        
        # Step 3: Import each video
        print(f"💾 Task {task_id}: Importing videos to database...")
        for idx, video_data in enumerate(videos_metadata, 1):
            try:
                progress["current_video"] = video_data["title"]
                
                # Check for duplicates
                is_duplicate = await GroupVideoCRUD.check_duplicate(
                    db, playlist_id, video_data["youtube_id"]
                )
                
                if is_duplicate:
                    progress["skipped_duplicates"] += 1
                    print(f"⏭️ Skipped duplicate: {video_data['title']}")
                else:
                    # Create video entry
                    video_create = GroupVideoCreate(
                        **video_data,
                        user_description=None,
                        position=idx
                    )
                    
                    await GroupVideoCRUD.create(db, playlist_id, video_create, added_by_id)
                    progress["imported"] += 1
                    print(f"✅ Imported: {video_data['title']}")
                
                # Update progress
                progress["progress_percentage"] = int((idx / len(videos_metadata)) * 100)
                set_cached_data(cache_key, progress, ttl=3600)
                
            except Exception as e:
                progress["failed"] += 1
                print(f"❌ Failed to import video: {str(e)}")
                continue
        
        # Task completed
        progress["status"] = "completed"
        progress["current_video"] = None
        progress["progress_percentage"] = 100
        set_cached_data(cache_key, progress, ttl=3600)
        
        print(f"✅ Task {task_id} completed: {progress['imported']} imported, "
              f"{progress['skipped_duplicates']} duplicates, {progress['failed']} failed")
        
    except Exception as e:
        # Task failed
        progress["status"] = "failed"
        progress["error"] = str(e)
        set_cached_data(cache_key, progress, ttl=3600)
        print(f"❌ Task {task_id} failed: {str(e)}")



async def import_playlist_simple(
    db: AsyncSession,
    playlist_id: int,
    youtube_playlist_url: str,
    added_by_id: int,
    max_videos: int = 50
):
    """Simple bulk import without progress tracking"""
    from utils.youtube import get_playlist_video_ids, get_videos_metadata_batch
    from crud.video import VideoCRUD
    from schemas.video import VideoCreate
    
    # Get playlist video IDs
    playlist_data = await get_playlist_video_ids(youtube_playlist_url, max_results=max_videos)
    video_ids = playlist_data["video_ids"]
    
    # Fetch metadata in batch
    videos_metadata = await get_videos_metadata_batch(video_ids)
    
    # Import each video
    for idx, video_data in enumerate(videos_metadata, 1):
        # Check duplicate
        is_duplicate = await VideoCRUD.check_duplicate(db, playlist_id, video_data["youtube_id"])
        
        if not is_duplicate:
            video_create = VideoCreate(**video_data, user_description=None, position=idx)
            await VideoCRUD.create(db, video_create, playlist_id, added_by_id)        