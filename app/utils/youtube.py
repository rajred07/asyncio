# import httpx
# from fastapi import HTTPException
# import os

# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

# async def extract_video_id(url: str) -> str:
#     """Extract video ID from various YouTube URL formats"""
#     video_id = None
#     if "youtu.be/" in url:
#         video_id = url.split("youtu.be/")[1].split("?")[0]
#     elif "v=" in url:
#         video_id = url.split("v=")[1].split("&")[0]
#     elif "youtube.com/embed/" in url:
#         video_id = url.split("embed/")[1].split("?")[0]
    
#     if not video_id:
#         raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
#     return video_id

# async def get_video_metadata(youtube_url: str):
#     """Fetch video metadata from YouTube API"""
#     video_id = await extract_video_id(youtube_url)
    
#     api_url = "https://www.googleapis.com/youtube/v3/videos"
#     params = {
#         "part": "snippet,statistics",
#         "id": video_id,
#         "key": YOUTUBE_API_KEY
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.get(api_url, params=params)
        
#         if response.status_code != 200:
#             raise HTTPException(status_code=500, detail="Failed to fetch from YouTube")
        
#         data = response.json()
    
#     if "items" not in data or len(data["items"]) == 0:
#         raise HTTPException(status_code=404, detail="Video not found on YouTube")
    
#     snippet = data["items"][0]["snippet"]
#     statistics = data["items"][0].get("statistics", {})
    
#     return {
#         "youtube_id": video_id,
#         "title": snippet["title"],
#         "channel_name": snippet.get("channelTitle", "Unknown"),
#         "thumbnail": snippet["thumbnails"]["high"]["url"],
#         "views": int(statistics.get("viewCount", 0)),
#         "youtube_description": snippet.get("description", "")
import httpx
from fastapi import HTTPException
import os
import time
from utils.cache import generate_cache_key, get_cached_data, set_cached_data

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")


def parse_iso8601_duration(duration_str: str) -> int:
    """
    Parse ISO 8601 duration string (e.g. PT4M13S) into total seconds.
    Examples: PT1H2M3S -> 3723, PT45S -> 45, P1DT2H -> 93600
    """
    import re
    if not duration_str:
        return 0
    pattern = re.compile(
        r'P(?:(?P<days>\d+)D)?'
        r'(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?'
    )
    match = pattern.match(duration_str)
    if not match:
        return 0
    parts = match.groupdict(default=0)
    return (
        int(parts['days'])    * 86400 +
        int(parts['hours'])   * 3600  +
        int(parts['minutes']) * 60    +
        int(parts['seconds'])
    )

async def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    video_id = None
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtube.com/embed/" in url:
        video_id = url.split("embed/")[1].split("?")[0]
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    return video_id

async def get_video_metadata(youtube_url: str, use_cache: bool = True):
    """
    Fetch video metadata from YouTube API with Redis caching
    
    Args:
        youtube_url: YouTube video URL
        use_cache: Whether to use cache (default: True, set False to force refresh)
    """
    start_time = time.time()
    
    # Extract Video ID
    video_id = await extract_video_id(youtube_url)
    
    # Check Cache First 🚀
    if use_cache:
        cache_key = generate_cache_key("youtube:video", video_id)
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            elapsed = (time.time() - start_time) * 1000
            print(f"✅ CACHE HIT for {video_id} ({elapsed:.2f}ms)")
            return cached_data
    
    # Cache Miss - Call YouTube API
    print(f"⚠️ CACHE MISS for {video_id} - Calling YouTube API...")
    
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch from YouTube")
        
        data = response.json()
    
    if "items" not in data or len(data["items"]) == 0:
        raise HTTPException(status_code=404, detail="Video not found on YouTube")
    
    snippet = data["items"][0]["snippet"]
    statistics = data["items"][0].get("statistics", {})
    
    video_data = {
        "youtube_id": video_id,
        "title": snippet["title"],
        "channel_name": snippet.get("channelTitle", "Unknown"),
        "thumbnail": snippet["thumbnails"]["high"]["url"],
        "views": int(statistics.get("viewCount", 0)),
        "duration": parse_iso8601_duration(
            data["items"][0].get("contentDetails", {}).get("duration", "PT0S")
        ),
        "youtube_description": snippet.get("description", "")
    }
    
    # Store in Cache 💾
    if use_cache:
        cache_key = generate_cache_key("youtube:video", video_id)
        set_cached_data(cache_key, video_data)
        print(f"💾 Cached video {video_id} for 7 days")
    
    elapsed = (time.time() - start_time) * 1000
    print(f"⏱️ YouTube API call took {elapsed:.2f}ms")
    
    return video_data


async def extract_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube playlist URL"""
    playlist_id = None
    if "list=" in url:
        playlist_id = url.split("list=")[1].split("&")[0]
    
    if not playlist_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube playlist URL")
    
    return playlist_id


async def get_playlist_video_ids(playlist_url: str, max_results: int = 50) -> dict:
    """
    Fetch video IDs from a YouTube playlist
    Returns: {
        "playlist_id": str,
        "video_ids": List[str],
        "total_count": int
    }
    """
    playlist_id = await extract_playlist_id(playlist_url)
    
    # Check cache for playlist video IDs
    cache_key = generate_cache_key("youtube:playlist_ids", playlist_id)
    cached_ids = get_cached_data(cache_key)
    
    if cached_ids:
        print(f"✅ CACHE HIT for playlist IDs {playlist_id}")
        return cached_ids
    
    print(f"⚠️ Fetching playlist {playlist_id} from YouTube API...")
    
    api_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    all_video_ids = []
    next_page_token = None
    
    async with httpx.AsyncClient() as client:
        while True:
            params = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": min(max_results, 50),  # YouTube API max is 50
                "key": YOUTUBE_API_KEY
            }
            
            if next_page_token:
                params["pageToken"] = next_page_token
            
            response = await client.get(api_url, params=params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch playlist from YouTube"
                )
            
            data = response.json()
            
            if "items" not in data:
                break
            
            # Extract video IDs
            for item in data["items"]:
                snippet = item.get("snippet", {})
                # Skip private/deleted videos
                if snippet.get("title") == "Private video" or "resourceId" not in snippet:
                    continue
                
                video_id = snippet["resourceId"]["videoId"]
                all_video_ids.append(video_id)
            
            # Check if there are more pages
            next_page_token = data.get("nextPageToken")
            if not next_page_token or len(all_video_ids) >= max_results:
                break
    
    result = {
        "playlist_id": playlist_id,
        "video_ids": all_video_ids[:max_results],
        "total_count": len(all_video_ids)
    }
    
    # Cache the playlist video IDs for 1 hour
    set_cached_data(cache_key, result, ttl=3600)
    print(f"💾 Cached playlist {playlist_id} with {len(all_video_ids)} videos")
    
    return result


async def get_videos_metadata_batch(video_ids: list[str]) -> list[dict]:
    """
    Fetch metadata for multiple videos efficiently (batch API call)
    YouTube API allows up to 50 video IDs per request
    """
    if not video_ids:
        return []
    
    all_videos_data = []
    
    # Split into batches of 50 (YouTube API limit)
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch_ids),
            "key": YOUTUBE_API_KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch batch {i//50 + 1}")
                continue
            
            data = response.json()
            
            if "items" not in data:
                continue
            
            for item in data["items"]:
                snippet = item["snippet"]
                statistics = item.get("statistics", {})
                
                video_data = {
                    "youtube_id": item["id"],
                    "title": snippet["title"],
                    "channel_name": snippet.get("channelTitle", "Unknown"),
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "views": int(statistics.get("viewCount", 0)),
                    "duration": parse_iso8601_duration(
                        item.get("contentDetails", {}).get("duration", "PT0S")
                    ),
                    "youtube_description": snippet.get("description", "")
                }
                
                all_videos_data.append(video_data)
                
                # Cache individual videos
                cache_key = generate_cache_key("youtube:video", item["id"])
                set_cached_data(cache_key, video_data)
        
        print(f"✅ Fetched batch {i//50 + 1}: {len(batch_ids)} videos")
    
    return all_videos_data