"""
============================================================
EaTube - Watch Later Processing Pipeline
============================================================
Reads watchlater.json → Enriches → Computes Features →
Categorizes via Gemini → Validates → Generates Playlists

Usage:
  1. Add your API keys to config.py
  2. pip install -r requirements.txt
  3. python process_watchlater.py
============================================================
"""

import json
import re
import time
import math
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

import requests
from google import genai
from google.genai import types as genai_types

from utils.config import (
    YOUTUBE_API_KEY,
    GEMINI_API_KEY,
    VIDEO_LIMIT,
    WATCHLATER_PATH,
    ENRICHED_OUTPUT_PATH,
    PLAYLISTS_OUTPUT_PATH,
    GEMINI_MODEL,
    YOUTUBE_API_BATCH_SIZE,
    GEMINI_BATCH_SIZE,
    YOUTUBE_CATEGORIES,
    LOCKED_CATEGORIES,
    MOOD_TAGS,
    VIEWING_TIMES,
    VIEWING_CONTEXTS,
)


# ============================================================
# UTILITIES
# ============================================================

def print_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_step(step_num, message):
    """Print a numbered step."""
    print(f"  [{step_num}] {message}")


def parse_scraped_duration(duration_str):
    """
    Parse duration strings from the Chrome extension scrape.
    Handles formats: "3:37", "38:34", "4:02:07", "8,785:27:03", "0:33"
    Returns duration in seconds, or 0 if unparseable.
    """
    if not duration_str or not isinstance(duration_str, str):
        return 0

    # Remove commas (handles "8,785:27:03")
    duration_str = duration_str.replace(",", "")
    parts = duration_str.strip().split(":")

    try:
        if len(parts) == 2:
            # MM:SS
            minutes, seconds = int(parts[0]), int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # H:MM:SS
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 1:
            return int(parts[0])
    except (ValueError, IndexError):
        pass

    return 0


def parse_iso_duration(iso_duration):
    """
    Parse ISO 8601 duration (from YouTube API) to seconds.
    Example: "PT3M37S" → 217, "PT1H2M30S" → 3750
    """
    if not iso_duration:
        return 0

    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
        iso_duration
    )
    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds):
    """Format seconds to human readable duration string."""
    if seconds <= 0:
        return "0:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def categorize_duration(seconds):
    """Categorize video by duration."""
    if seconds <= 0:
        return "Unknown"
    if seconds < 60:
        return "Short"          # YouTube Shorts, clips
    elif seconds < 300:
        return "Quick"          # Quick watch, music videos
    elif seconds < 600:
        return "Standard"       # Normal videos
    elif seconds < 1200:
        return "Medium"         # Detailed content
    elif seconds < 3600:
        return "Long"           # In-depth, tutorials
    else:
        return "Very Long"      # Movies, streams, compilations


def suggest_viewing_context(duration_category):
    """Suggest viewing context based on duration."""
    contexts = {
        "Short": "Coffee break, Waiting room",
        "Quick": "Commute, Quick break",
        "Standard": "Lunch break, Evening relax",
        "Medium": "Afternoon, Focus time",
        "Long": "Weekend, Deep focus session",
        "Very Long": "Weekend binge, Background",
        "Unknown": "Anytime",
    }
    return contexts.get(duration_category, "Anytime")


def categorize_video_age(days):
    """Categorize video by age."""
    if days < 30:
        return "Fresh"
    elif days < 180:
        return "Recent"
    elif days < 730:
        return "Standard"
    elif days < 1825:
        return "Classic"
    else:
        return "Vintage"


def categorize_watchlater_freshness(days):
    """How long the video has been in Watch Later."""
    if days < 7:
        return "New"
    elif days < 30:
        return "Aging"
    else:
        return "Stale"


def categorize_popularity(view_count):
    """Categorize video by view count."""
    if view_count >= 100_000_000:
        return "Viral"
    elif view_count >= 10_000_000:
        return "Very Popular"
    elif view_count >= 1_000_000:
        return "Popular"
    elif view_count >= 100_000:
        return "Moderate"
    else:
        return "Niche"


def detect_language(text):
    """
    Detect languages in text using script analysis.
    Returns list of detected languages.
    """
    if not text:
        return ["Unknown"]

    languages = []

    # Check for Devanagari script (Hindi / Marathi)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        languages.append("Hindi/Marathi")

    # Check for Latin script (English)
    latin_pattern = re.compile(r'[a-zA-Z]{3,}')
    if latin_pattern.search(text):
        languages.append("English")

    if not languages:
        languages.append("Unknown")

    return languages


def categorize_language(languages):
    """Categorize the language mix."""
    if languages == ["English"]:
        return "Pure English"
    elif languages == ["Hindi/Marathi"]:
        return "Pure Hindi/Marathi"
    elif "Hindi/Marathi" in languages and "English" in languages:
        return "Mixed (Hinglish)"
    return "Unknown"


def guess_content_type(title, channel_name, category_id=None):
    """
    Rule-based content type detection from title and channel.
    Returns a best-guess content type string.
    """
    title_lower = (title or "").lower()
    channel_lower = (channel_name or "").lower()

    # Music indicators
    music_keywords = [
        "official music video", "official video", "lyric video", "lyrics",
        "audio", "full song", "song video", "jukebox", "hit song",
        "cover", "unplugged", "remix", "stotram", "bhajan", "qawali",
    ]
    music_channels = [
        "t-series", "zee music", "sony music", "saregama", "yrf",
        "tips official", "bollywood classics", "sufiscore",
    ]
    if any(kw in title_lower for kw in music_keywords) or \
       any(ch in channel_lower for ch in music_channels) or \
       category_id == "10":
        return "music"

    # Gaming — only actual gameplay/gaming content, NOT animation titles
    gaming_keywords = [
        "gameplay", "walkthrough", "pubg mobile", "brawl stars",
        "clash of clans", "clash royale", "free fire gameplay",
        "chicken dinner", "gaming highlights", "play minecraft",
        "let's play", "game review", "esports",
    ]
    # Avoid false positives: "Animation vs Minecraft" is NOT a gaming video
    is_animation = any(w in title_lower for w in ["animation vs", "alan becker"])
    if not is_animation and (
        any(kw in title_lower for kw in gaming_keywords) or category_id == "20"
    ):
        return "gaming"

    # Comedy
    comedy_keywords = [
        "funny", "comedy", "roast", "memes", "vines", "prank",
        "triggered", "thugesh", "rawknee", "slayy point",
    ]
    comedy_channels = [
        "bb ki vines", "carryminati", "triggered insaan", "ashish chanchlani",
        "tanmay bhat", "angry prash", "slayy point", "saiman says",
    ]
    if any(kw in title_lower for kw in comedy_keywords) or \
       any(ch in channel_lower for ch in comedy_channels) or \
       category_id == "23":
        return "comedy"

    # Food & Cooking
    food_keywords = [
        "recipe", "cooking", "kitchen", "food", "khana", "masala",
        "biryani", "dosa", "gulabjamun", "vada pav", "dhokla", "chakli",
    ]
    if any(kw in title_lower for kw in food_keywords):
        return "food"

    # Sports
    sports_keywords = [
        "cricket", "ipl", "dhoni", "kohli", "sports", "match",
        "world cup", "football", "trick shots",
    ]
    if any(kw in title_lower for kw in sports_keywords) or category_id == "17":
        return "sports"

    # Education / Info
    edu_keywords = [
        "tutorial", "how to", "guide", "learn", "course", "explained",
        "facts", "top 5", "top 10", "history", "science",
    ]
    if any(kw in title_lower for kw in edu_keywords) or category_id == "27":
        return "education"

    # Movies / Superheroes
    movie_keywords = [
        "avengers", "marvel", "mcu", "endgame", "spider-man", "trailer",
        "movie", "iron man", "thanos", "thor", "black widow",
    ]
    if any(kw in title_lower for kw in movie_keywords):
        return "movies_superheroes"

    return "other"


# ============================================================
# LAYER 1: PARSE & ENRICH (YouTube Data API)
# ============================================================

def load_watchlater(path, limit):
    """Load and parse watchlater.json, return first N videos."""
    print_header("LAYER 1: Parse & Enrich via YouTube API")
    print_step(1, f"Loading {path}...")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data.get("videos", [])
    total = len(videos)
    selected = videos[:limit]

    print_step(2, f"Total videos in file: {total}")
    print_step(3, f"Processing first {len(selected)} videos")
    print()

    return selected, data.get("scrapedAt", "")


def fetch_youtube_metadata(video_ids, api_key):
    """
    Fetch rich metadata from YouTube Data API v3.
    Batches requests (max 50 IDs per call).
    Returns dict: {videoId: api_data}
    """
    if api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        print("  ⚠️  No YouTube API key set. Skipping API enrichment.")
        print("  ⚠️  Add your key to config.py to enable this.")
        return {}

    all_data = {}
    batches = [video_ids[i:i + YOUTUBE_API_BATCH_SIZE]
               for i in range(0, len(video_ids), YOUTUBE_API_BATCH_SIZE)]

    for batch_idx, batch in enumerate(batches):
        ids_str = ",".join(batch)
        url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,contentDetails,statistics,status"
            f"&id={ids_str}"
            f"&key={api_key}"
        )

        print_step(4, f"YouTube API batch {batch_idx + 1}/{len(batches)} "
                      f"({len(batch)} videos)...")

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                vid_id = item["id"]
                snippet = item.get("snippet", {})
                content = item.get("contentDetails", {})
                stats = item.get("statistics", {})
                status = item.get("status", {})

                all_data[vid_id] = {
                    "snippet": {
                        "publishedAt": snippet.get("publishedAt", ""),
                        "channelId": snippet.get("channelId", ""),
                        "description": (snippet.get("description", "") or "")[:500],
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", ""),
                        "defaultLanguage": snippet.get("defaultLanguage", ""),
                        "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
                    },
                    "contentDetails": {
                        "duration": content.get("duration", ""),
                        "dimension": content.get("dimension", ""),
                        "definition": content.get("definition", ""),
                        "caption": content.get("caption", "false"),
                    },
                    "statistics": {
                        "viewCount": int(stats.get("viewCount", 0)),
                        "likeCount": int(stats.get("likeCount", 0)),
                        "commentCount": int(stats.get("commentCount", 0)),
                    },
                    "status": {
                        "uploadStatus": status.get("uploadStatus", ""),
                        "privacyStatus": status.get("privacyStatus", ""),
                        "madeForKids": status.get("madeForKids", False),
                    },
                }

            print(f"       ✅ Got data for {len(data.get('items', []))} videos")

        except requests.exceptions.RequestException as e:
            print(f"       ❌ API Error: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            print(f"       ❌ Parse Error: {e}")

        # Small delay between batches
        if batch_idx < len(batches) - 1:
            time.sleep(0.5)

    return all_data


# ============================================================
# LAYER 2: FEATURE ENGINEERING
# ============================================================

def compute_features(videos, youtube_data, scraped_at):
    """
    Compute all derived features for each video.
    Merges scraped data + YouTube API data + computed fields.
    """
    print_header("LAYER 2: Feature Engineering")

    today = datetime.now(timezone.utc)
    enriched = []

    for idx, video in enumerate(videos):
        vid_id = video["videoId"]
        api = youtube_data.get(vid_id, {})
        snippet = api.get("snippet", {})
        content_details = api.get("contentDetails", {})
        stats = api.get("statistics", {})
        status = api.get("status", {})

        # -- Duration --
        # Prefer API ISO duration if available, else parse scraped string
        if content_details.get("duration"):
            duration_seconds = parse_iso_duration(content_details["duration"])
        else:
            duration_seconds = parse_scraped_duration(video.get("duration", ""))

        duration_cat = categorize_duration(duration_seconds)
        viewing_ctx = suggest_viewing_context(duration_cat)

        # -- Published Date & Age --
        published_at = snippet.get("publishedAt", "")
        video_age_days = 0
        video_age_cat = "Unknown"
        if published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                video_age_days = (today - pub_date).days
                video_age_cat = categorize_video_age(video_age_days)
            except (ValueError, TypeError):
                pass

        # -- Watch Later Freshness --
        saved_at = video.get("scrapedAt", scraped_at)
        days_in_wl = 0
        wl_freshness = "Unknown"
        if saved_at:
            try:
                save_date = datetime.fromisoformat(saved_at.replace("Z", "+00:00"))
                days_in_wl = (today - save_date).days
                wl_freshness = categorize_watchlater_freshness(days_in_wl)
            except (ValueError, TypeError):
                pass

        # -- Engagement --
        view_count = stats.get("viewCount", 0)
        like_count = stats.get("likeCount", 0)
        comment_count = stats.get("commentCount", 0)

        engagement_rate = 0.0
        like_ratio = 0.0
        if view_count > 0:
            engagement_rate = (like_count + comment_count) / view_count
            like_ratio = like_count / view_count

        popularity_tier = categorize_popularity(view_count) if view_count > 0 else "Unknown"
        quality_indicator = "High Quality" if like_ratio > 0.04 else "Standard"

        # -- Language --
        title = video.get("title", "")
        detected_langs = detect_language(title)
        lang_category = categorize_language(detected_langs)

        # -- YouTube Category Name --
        category_id = snippet.get("categoryId", "")
        yt_cat_name = YOUTUBE_CATEGORIES.get(category_id, "Unknown")

        # -- Build enriched object --
        enriched_video = {
            "videoId": vid_id,
            "savedIndex": idx,

            "basic": {
                "title": title,
                "url": video.get("url", f"https://www.youtube.com/watch?v={vid_id}"),
                "channelName": video.get("channelName", "Unknown"),
                "channelId": snippet.get("channelId", ""),
                "thumbnail": video.get("thumbnail", ""),
            },

            "metadata": {
                "description": snippet.get("description", ""),
                "tags": snippet.get("tags", []),
                "publishedAt": published_at,
                "youtubeCategoryId": category_id,
                "youtubeCategoryName": yt_cat_name,
                "language": snippet.get("defaultAudioLanguage", "") or snippet.get("defaultLanguage", ""),
            },

            "videoProperties": {
                "durationScraped": video.get("duration", ""),
                "durationSeconds": duration_seconds,
                "durationFormatted": format_duration(duration_seconds),
                "isHD": content_details.get("definition", "") == "hd",
                "hasCaptions": content_details.get("caption", "false") == "true",
            },

            "engagement": {
                "viewCount": view_count,
                "likeCount": like_count,
                "commentCount": comment_count,
            },

            "status": {
                "privacyStatus": status.get("privacyStatus", "unknown"),
                "madeForKids": status.get("madeForKids", False),
            },

            "userContext": {
                "savedAt": saved_at,
                "savedIndex": idx,
            },

            "computed": {
                "videoAgeDays": video_age_days,
                "videoAgeCategory": video_age_cat,
                "daysInWatchLater": days_in_wl,
                "watchLaterFreshness": wl_freshness,
                "durationCategory": duration_cat,
                "suggestedViewingContext": viewing_ctx,
                "engagementRate": round(engagement_rate, 6),
                "popularityTier": popularity_tier,
                "likeRatio": round(like_ratio, 6),
                "qualityIndicator": quality_indicator,
                "detectedLanguages": detected_langs,
                "languageCategory": lang_category,
                "isShort": 0 < duration_seconds <= 60,  # YouTube Shorts threshold
            },
        }

        enriched.append(enriched_video)
        print_step(idx + 1, f"✅ {title[:60]}... | {duration_cat} | {lang_category}")

    print(f"\n  Feature engineering complete for {len(enriched)} videos")
    return enriched


# ============================================================
# LAYER 3: GEMINI CATEGORIZATION
# ============================================================

def build_gemini_prompt(videos_batch):
    """
    Build the Gemini categorization prompt.
    Passes the FULL enriched JSON for each video — Gemini decides category
    using all available signals (title, channel, tags, description, duration,
    YouTube category, language, engagement stats, etc.).
    No rule-based pre-categorization is applied.
    """
    categories_str = "\n".join(f"  - {cat}" for cat in LOCKED_CATEGORIES)
    moods_str = ", ".join(MOOD_TAGS)
    times_str = ", ".join(VIEWING_TIMES)
    contexts_str = ", ".join(VIEWING_CONTEXTS)

    # Serialize each video's full enriched data for Gemini
    # We omit only thumbnail URL and savedIndex (not useful for classification)
    videos_json_list = []
    for i, v in enumerate(videos_batch):
        video_data = {
            "index": i + 1,
            "title": v["basic"]["title"],
            "channel": v["basic"]["channelName"],
            "duration": v["videoProperties"]["durationFormatted"],
            "duration_seconds": v["videoProperties"]["durationSeconds"],
            "is_short": v["computed"]["isShort"],   # True if ≤60s (YouTube Short format)
            "is_hd": v["videoProperties"]["isHD"],
            "has_captions": v["videoProperties"]["hasCaptions"],
            "youtube_category": v["metadata"]["youtubeCategoryName"],
            "api_language": v["metadata"]["language"],
            "tags": v["metadata"]["tags"][:20],
            "description": (v["metadata"]["description"] or "")[:300],
            "published_at": v["metadata"]["publishedAt"],
            "view_count": v["engagement"]["viewCount"],
            "like_count": v["engagement"]["likeCount"],
            "comment_count": v["engagement"]["commentCount"],
            "video_age_category": v["computed"]["videoAgeCategory"],
            "duration_category": v["computed"]["durationCategory"],
            "popularity_tier": v["computed"]["popularityTier"],
            "detected_languages": v["computed"]["detectedLanguages"],
            "language_category": v["computed"]["languageCategory"],
            "engagement_rate": v["computed"]["engagementRate"],
        }
        videos_json_list.append(video_data)

    videos_json_str = json.dumps(videos_json_list, ensure_ascii=False, indent=2)

    prompt = f"""You are an expert YouTube content analyst categorizing videos from an Indian user's Watch Later playlist.

You will receive the FULL enriched data for each video as JSON. Use ALL available signals — title, channel name, tags, description, YouTube category, language, duration, view count, etc. — to make the most accurate categorization.

DO NOT rely only on the title. Use the full context.
If `is_short` is true, this is a YouTube Short (≤60 seconds). Treat it the same as a normal video for category purposes, but note it is short-form content in secondary_tags with the tag "Short".

RULES (FOLLOW STRICTLY):
1. Use ONLY these primary categories:
{categories_str}
2. Use ONLY these mood tags (pick 1-3): {moods_str}
3. Use ONLY these viewing times: {times_str}
4. Use ONLY these "best_for" contexts: {contexts_str}
5. Return ONLY a valid JSON array. No text before or after the JSON.
6. One JSON object per video, in the SAME ORDER as input.
7. "summary" must be a 1-sentence description of what the video actually is about.
8. "confidence" should reflect how certain you are (0.0–1.0). Be honest.

FEW-SHOT EXAMPLES (for output format):

Input video: {{"title": "Teri Mitti - Lyrical | Kesari", "channel": "Zee Music Company", "youtube_category": "Music", "language_category": "Mixed (Hinglish)", "tags": ["kesari", "akshay kumar", "b praak"], "is_short": false}}
→ {{"primary_category": "Bollywood & Hindi Music", "secondary_tags": ["Patriotic", "Emotional", "Movie Song"], "mood_tags": ["Inspiring", "Emotional"], "viewing_context": {{"best_time": "Evening", "best_for": "Relax"}}, "summary": "Patriotic Bollywood ballad from the 2019 movie Kesari featuring Akshay Kumar.", "confidence": 0.97}}

Input video: {{"title": "BB Ki Vines- | Maun Vrat |", "channel": "BB Ki Vines", "youtube_category": "Comedy", "language_category": "Mixed (Hinglish)", "duration": "5:03", "is_short": false}}
→ {{"primary_category": "Comedy & Roast", "secondary_tags": ["Indian Comedy", "Sketch", "Hinglish"], "mood_tags": ["Funny", "Happy"], "viewing_context": {{"best_time": "Evening", "best_for": "Relax"}}, "summary": "Hindi comedy sketch by popular Indian YouTuber Bhuvan Bam about staying silent.", "confidence": 0.98}}

Input video: {{"title": "Quick Cricket Highlight", "channel": "SportsBuzz", "youtube_category": "Sports", "duration": "0:45", "is_short": true}}
→ {{"primary_category": "Sports & Cricket", "secondary_tags": ["Short", "Highlight"], "mood_tags": ["Exciting"], "viewing_context": {{"best_time": "Anytime", "best_for": "Relax"}}, "summary": "A short-form sports highlight clip.", "confidence": 0.9}}

Input video: {{"title": "Animation vs. Minecraft Shorts Season 2", "channel": "Alan Becker", "youtube_category": "Film & Animation", "language_category": "Pure English", "duration": "38:34", "is_short": false, "tags": ["animation", "alan becker", "animator vs animation"]}}
→ {{"primary_category": "Entertainment & Pop Culture", "secondary_tags": ["Animation", "Action", "Compilation"], "mood_tags": ["Exciting", "Funny"], "viewing_context": {{"best_time": "Weekend", "best_for": "Relax"}}, "summary": "Animated action-comedy compilation by Alan Becker featuring stick figures in a Minecraft world.", "confidence": 0.95}}

NOW CATEGORIZE THESE {len(videos_batch)} VIDEOS (full enriched data below):
{videos_json_str}

Return a JSON array of exactly {len(videos_batch)} objects, each with these keys:
primary_category, secondary_tags, mood_tags, viewing_context (object with best_time and best_for), summary, confidence"""

    return prompt


def categorize_with_gemini(enriched_videos, api_key):
    """
    Send videos to Gemini for AI categorization.
    Processes in batches of GEMINI_BATCH_SIZE.
    """
    print_header("LAYER 3: Gemini AI Categorization")

    if api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("  ⚠️  No Gemini API key set. Using rule-based fallback only.")
        print("  ⚠️  Add your key to config.py to enable AI categorization.")
        # Apply fallback categorization
        for v in enriched_videos:
            v["gemini"] = create_fallback_categorization(v)
        return enriched_videos

    # Configure Gemini client
    client = genai.Client(api_key=api_key)

    # Process in batches
    batches = [enriched_videos[i:i + GEMINI_BATCH_SIZE]
               for i in range(0, len(enriched_videos), GEMINI_BATCH_SIZE)]

    for batch_idx, batch in enumerate(batches):
        print_step(batch_idx + 1, f"Gemini batch {batch_idx + 1}/{len(batches)} "
                                  f"({len(batch)} videos)...")

        prompt = build_gemini_prompt(batch)

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,      # Low temp for consistency
                    max_output_tokens=16384,  # Increased to prevent JSON truncation
                ),
            )

            # Parse JSON from response
            response_text = response.text.strip()

            # Clean markdown code fences if present
            if response_text.startswith("```"):
                response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            categories = json.loads(response_text)

            if isinstance(categories, list) and len(categories) == len(batch):
                for v, cat in zip(batch, categories):
                    v["gemini"] = {
                        "primaryCategory": cat.get("primary_category", "Other"),
                        "secondaryTags": cat.get("secondary_tags", []),
                        "moodTags": cat.get("mood_tags", []),
                        "viewingContext": cat.get("viewing_context", {}),
                        "summary": cat.get("summary", ""),
                        "confidence": cat.get("confidence", 0.5),
                    }
                    print(f"       ✅ {v['basic']['title'][:50]}... → {v['gemini']['primaryCategory']}")
            else:
                print(f"       ⚠️  Gemini returned {len(categories) if isinstance(categories, list) else 'invalid'} "
                      f"items, expected {len(batch)}. Using fallback.")
                for v in batch:
                    v["gemini"] = create_fallback_categorization(v)

        except json.JSONDecodeError as e:
            print(f"       ❌ JSON parse error: {e}")
            print(f"       Raw response: {response_text[:200]}...")
            for v in batch:
                v["gemini"] = create_fallback_categorization(v)

        except Exception as e:
            print(f"       ❌ Gemini error: {e}")
            for v in batch:
                v["gemini"] = create_fallback_categorization(v)

        # Rate limiting
        if batch_idx < len(batches) - 1:
            time.sleep(1)

    return enriched_videos


def create_fallback_categorization(video):
    """
    Fallback when Gemini is unavailable or fails.
    Does NOT use any rule-based title/keyword guessing.
    Marks the video as Uncategorized so it can be identified and re-processed.
    """
    return {
        "primaryCategory": "Uncategorized",
        "secondaryTags": [],
        "moodTags": [],
        "viewingContext": {"best_time": "Anytime", "best_for": "Relax"},
        "summary": "Not categorized — add your Gemini API key to config.py and re-run.",
        "confidence": 0.0,
    }


# ============================================================
# LAYER 4: VALIDATION
# ============================================================

def validate_categorizations(enriched_videos):
    """
    Apply rule-based validation to catch Gemini mistakes.
    Adds a 'validated' field to each video.
    """
    print_header("LAYER 4: Validation & Post-Processing")

    # Known channel → category overrides
    # Note: these run LAST and take highest priority
    channel_overrides = {
        "t-series": "Bollywood & Hindi Music",
        "zee music company": "Bollywood & Hindi Music",
        "sony music india": "Bollywood & Hindi Music",
        "saregama music": "Bollywood & Hindi Music",
        "saregama marathi": "Marathi Music & Culture",
        "zee music marathi": "Marathi Music & Culture",
        "bb ki vines": "Comedy & Roast",
        "carryminati": "Comedy & Roast",
        "triggered insaan": "Comedy & Roast",
        "ashish chanchlani vines": "Comedy & Roast",
        "tanmay bhat": "Comedy & Roast",
        "angry prash": "Comedy & Roast",
        "slayy point": "Comedy & Roast",
        "saiman says": "Comedy & Roast",
        "thugesh": "Comedy & Roast",
        "dude perfect": "Entertainment & Pop Culture",   # Trick shots ≠ cricket
        "brawl stars": "Gaming",
        "clash of clans": "Gaming",
        "times music spiritual": "Indian Classical & Devotional",
    }

    # YouTube category cross-check mapping (used as a flag only, not an override)
    yt_cat_to_locked = {
        "Music": ["Bollywood & Hindi Music", "Western & English Music",
                   "Marathi Music & Culture", "Indian Classical & Devotional"],
        "Gaming": ["Gaming"],
        "Comedy": ["Comedy & Roast"],
        "Sports": ["Sports & Cricket"],
        "Education": ["Education & Information"],
    }

    stats = {"high": 0, "medium": 0, "low": 0, "overridden": 0}

    for v in enriched_videos:
        gemini = v.get("gemini", {})
        gemini_cat = gemini.get("primaryCategory", "Other")
        gemini_conf = gemini.get("confidence", 0.5)
        flags = []
        overrides = []
        final_category = gemini_cat
        source = "gemini"

        channel_lower = v["basic"]["channelName"].lower()
        yt_cat_name = v["metadata"]["youtubeCategoryName"]
        duration_secs = v["videoProperties"]["durationSeconds"]

        # Rule: Channel override — only for well-known Indian channels
        # where Gemini is statistically likely to be wrong (e.g. misreads Hinglish)
        if channel_lower in channel_overrides:
            expected = channel_overrides[channel_lower]
            if final_category != expected:
                overrides.append(f"Channel '{v['basic']['channelName']}' → {expected}")
                final_category = expected
                source = "channel_override"

        # Rule 3: YouTube category cross-check
        if yt_cat_name in yt_cat_to_locked:
            valid_cats = yt_cat_to_locked[yt_cat_name]
            if final_category not in valid_cats and source == "gemini":
                flags.append(f"YouTube says '{yt_cat_name}' but Gemini says '{final_category}'")
                gemini_conf *= 0.8  # Penalty

        # Rule 4: Duration sanity
        if duration_secs > 3600 and final_category in ["Comedy & Roast"]:
            flags.append(f"Duration {format_duration(duration_secs)} unusual for {final_category}")
            gemini_conf *= 0.9

        # Rule 5: Shorts detection
        is_short = duration_secs < 60 and duration_secs > 0

        # Calculate final confidence
        if overrides:
            validation_score = 0.95  # Overrides are high confidence
        else:
            validation_score = gemini_conf

        # Determine tier
        if validation_score > 0.85:
            tier = "High Confidence"
            stats["high"] += 1
        elif validation_score > 0.65:
            tier = "Medium Confidence"
            stats["medium"] += 1
        else:
            tier = "Low Confidence"
            stats["low"] += 1

        if overrides:
            stats["overridden"] += 1

        v["validated"] = {
            "finalCategory": final_category,
            "categorySource": source,
            "validationScore": round(validation_score, 2),
            "validationTier": tier,
            "flags": flags,
            "overrides": overrides,
            "isShort": is_short,
        }

        status_icon = "🔄" if overrides else "✅"
        print_step("•", f"{status_icon} {v['basic']['title'][:50]}... → {final_category} ({tier})")

    print(f"\n  Validation Summary:")
    print(f"    High Confidence:  {stats['high']}")
    print(f"    Medium Confidence: {stats['medium']}")
    print(f"    Low Confidence:   {stats['low']}")
    print(f"    Overridden:       {stats['overridden']}")

    return enriched_videos


# ============================================================
# LAYER 5: PLAYLIST GENERATION
# ============================================================

def generate_playlists(enriched_videos):
    """
    Group validated videos into smart playlists.
    """
    print_header("LAYER 5: Playlist Generation")

    # Step 1: Group by final category
    category_groups = defaultdict(list)
    for v in enriched_videos:
        cat = v["validated"]["finalCategory"]
        category_groups[cat].append(v)

    print_step(1, "Category distribution:")
    for cat, vids in sorted(category_groups.items(), key=lambda x: -len(x[1])):
        print(f"       {cat}: {len(vids)} videos")

    playlists = []

    # Step 2: Create category-based playlists (exclude Shorts — they get their own playlist)
    shorts = [v for v in enriched_videos if v["computed"]["isShort"]]
    non_shorts = [v for v in enriched_videos if not v["computed"]["isShort"]]

    # Re-group without Shorts
    category_groups_no_shorts = defaultdict(list)
    for v in non_shorts:
        cat = v["validated"]["finalCategory"]
        category_groups_no_shorts[cat].append(v)

    for cat, vids in category_groups_no_shorts.items():
        if len(vids) < 1:
            continue

        # Sort by engagement (views as proxy when we have stats)
        vids_sorted = sorted(
            vids,
            key=lambda x: x["engagement"]["viewCount"],
            reverse=True
        )

        # Calculate total duration
        total_duration = sum(v["videoProperties"]["durationSeconds"] for v in vids_sorted)
        avg_duration = total_duration // len(vids_sorted) if vids_sorted else 0

        # Collect dominant mood
        mood_counts = defaultdict(int)
        for v in vids_sorted:
            for mood in v.get("gemini", {}).get("moodTags", []):
                mood_counts[mood] += 1
        dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "Mixed"

        playlist = {
            "id": f"pl_{cat.lower().replace(' ', '_').replace('&', 'and')}",
            "title": f"{cat}",
            "description": (
                f"Auto-generated from your Watch Later playlist.\n"
                f"📊 {len(vids_sorted)} videos | "
                f"Total: {format_duration(total_duration)} | "
                f"Avg: {format_duration(avg_duration)}\n"
                f"🎭 Dominant mood: {dominant_mood}"
            ),
            "type": "category",
            "videoCount": len(vids_sorted),
            "totalDurationSeconds": total_duration,
            "totalDurationFormatted": format_duration(total_duration),
            "avgDurationFormatted": format_duration(avg_duration),
            "dominantMood": dominant_mood,
            "videos": [
                {
                    "position": pos + 1,
                    "videoId": v["videoId"],
                    "title": v["basic"]["title"],
                    "channelName": v["basic"]["channelName"],
                    "duration": v["videoProperties"]["durationFormatted"],
                    "durationSeconds": v["videoProperties"]["durationSeconds"],
                    "viewCount": v["engagement"]["viewCount"],
                    "url": v["basic"]["url"],
                    "summary": v.get("gemini", {}).get("summary", ""),
                    "moodTags": v.get("gemini", {}).get("moodTags", []),
                }
                for pos, v in enumerate(vids_sorted)
            ],
        }
        playlists.append(playlist)

    # Step 3: Create smart cross-category playlists
    smart_playlists = []

    # YouTube Shorts playlist (all ≤60s videos)
    if shorts:
        shorts_sorted = sorted(shorts, key=lambda x: x["engagement"]["viewCount"], reverse=True)
        total_dur = sum(v["videoProperties"]["durationSeconds"] for v in shorts_sorted)
        smart_playlists.append({
            "id": "pl_youtube_shorts",
            "title": "📱 YouTube Shorts",
            "description": f"Short-form content (≤60 seconds).\n📊 {len(shorts_sorted)} videos | Total: {format_duration(total_dur)}",
            "type": "smart",
            "videoCount": len(shorts_sorted),
            "totalDurationFormatted": format_duration(total_dur),
            "videos": [
                {
                    "position": pos + 1,
                    "videoId": v["videoId"],
                    "title": v["basic"]["title"],
                    "channelName": v["basic"]["channelName"],
                    "duration": v["videoProperties"]["durationFormatted"],
                    "url": v["basic"]["url"],
                    "category": v["validated"]["finalCategory"],
                    "summary": v.get("gemini", {}).get("summary", ""),
                }
                for pos, v in enumerate(shorts_sorted)
            ],
        })

    # Quick Breaks playlist (5–20 min non-Shorts)
    quick_vids = [v for v in non_shorts
                  if 0 < v["videoProperties"]["durationSeconds"] < 300]
    if len(quick_vids) >= 2:
        quick_sorted = sorted(quick_vids,
                            key=lambda x: x["engagement"]["viewCount"],
                            reverse=True)
        total_dur = sum(v["videoProperties"]["durationSeconds"] for v in quick_sorted)
        smart_playlists.append({
            "id": "pl_quick_breaks",
            "title": "⚡ Quick Breaks (Under 5 min)",
            "description": f"Short videos perfect for a quick break.\n📊 {len(quick_sorted)} videos | Total: {format_duration(total_dur)}",
            "type": "smart",
            "videoCount": len(quick_sorted),
            "totalDurationFormatted": format_duration(total_dur),
            "videos": [
                {
                    "position": pos + 1,
                    "videoId": v["videoId"],
                    "title": v["basic"]["title"],
                    "channelName": v["basic"]["channelName"],
                    "duration": v["videoProperties"]["durationFormatted"],
                    "url": v["basic"]["url"],
                    "category": v["validated"]["finalCategory"],
                }
                for pos, v in enumerate(quick_sorted)
            ],
        })

    # Deep Dives playlist (videos > 20 min)
    long_vids = [v for v in enriched_videos
                 if v["videoProperties"]["durationSeconds"] > 1200]
    if len(long_vids) >= 2:
        long_sorted = sorted(long_vids,
                           key=lambda x: x["engagement"]["viewCount"],
                           reverse=True)
        total_dur = sum(v["videoProperties"]["durationSeconds"] for v in long_sorted)
        smart_playlists.append({
            "id": "pl_deep_dives",
            "title": "🎬 Weekend Deep Dives (20+ min)",
            "description": f"Long-form content for when you have time.\n📊 {len(long_sorted)} videos | Total: {format_duration(total_dur)}",
            "type": "smart",
            "videoCount": len(long_sorted),
            "totalDurationFormatted": format_duration(total_dur),
            "videos": [
                {
                    "position": pos + 1,
                    "videoId": v["videoId"],
                    "title": v["basic"]["title"],
                    "channelName": v["basic"]["channelName"],
                    "duration": v["videoProperties"]["durationFormatted"],
                    "url": v["basic"]["url"],
                    "category": v["validated"]["finalCategory"],
                }
                for pos, v in enumerate(long_sorted)
            ],
        })

    playlists.extend(smart_playlists)

    # Sort playlists by video count (largest first)
    playlists.sort(key=lambda p: p["videoCount"], reverse=True)

    # Step 4: Print summary
    print_step(2, f"\nGenerated {len(playlists)} playlists:")
    for pl in playlists:
        print(f"       📋 {pl['title']} ({pl['videoCount']} videos, {pl.get('totalDurationFormatted', '?')})")

    # Build final output
    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceVideoCount": len(enriched_videos),
        "playlistCount": len(playlists),
        "playlists": playlists,
        "stats": {
            "categoryDistribution": {
                cat: len(vids) for cat, vids in
                sorted(category_groups.items(), key=lambda x: -len(x[1]))
            },
            "totalVideos": len(enriched_videos),
            "totalDuration": format_duration(
                sum(v["videoProperties"]["durationSeconds"] for v in enriched_videos)
            ),
        },
    }

    return output


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    """Run the full processing pipeline."""
    print("\n" + "🎬" * 30)
    print("  EaTube - Watch Later Processing Pipeline")
    print("🎬" * 30)

    start_time = time.time()

    # --- Layer 1: Parse & Enrich ---
    videos, scraped_at = load_watchlater(WATCHLATER_PATH, VIDEO_LIMIT)
    video_ids = [v["videoId"] for v in videos]

    youtube_data = fetch_youtube_metadata(video_ids, YOUTUBE_API_KEY)
    print(f"\n  YouTube API returned data for {len(youtube_data)}/{len(video_ids)} videos")

    # --- Layer 2: Feature Engineering ---
    enriched = compute_features(videos, youtube_data, scraped_at)

    # --- Layer 3: Gemini Categorization ---
    enriched = categorize_with_gemini(enriched, GEMINI_API_KEY)

    # --- Layer 4: Validation ---
    enriched = validate_categorizations(enriched)

    # --- Save enriched data ---
    print_header("Saving Enriched Data")
    with open(ENRICHED_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "processedAt": datetime.now(timezone.utc).isoformat(),
            "totalProcessed": len(enriched),
            "videos": enriched,
        }, f, indent=2, ensure_ascii=False)
    print_step(1, f"✅ Saved enriched data → {ENRICHED_OUTPUT_PATH}")

    # --- Layer 5: Playlist Generation ---
    playlists_data = generate_playlists(enriched)

    with open(PLAYLISTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(playlists_data, f, indent=2, ensure_ascii=False)
    print_step(2, f"✅ Saved playlists → {PLAYLISTS_OUTPUT_PATH}")

    # --- Final Summary ---
    elapsed = time.time() - start_time
    print_header("🎉 Pipeline Complete!")
    print(f"  Processed: {len(enriched)} videos")
    print(f"  Playlists: {playlists_data['playlistCount']}")
    print(f"  Time: {elapsed:.1f} seconds")
    print(f"\n  Output files:")
    print(f"    📄 {ENRICHED_OUTPUT_PATH}")
    print(f"    📋 {PLAYLISTS_OUTPUT_PATH}")
    print(f"\n  Next steps:")
    print(f"    1. Check the output files")
    print(f"    2. If satisfied, change VIDEO_LIMIT to 310 in config.py")
    print(f"    3. Run again: python process_watchlater.py")
    print()


if __name__ == "__main__":
    main()
