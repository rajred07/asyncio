"""
URL utility helpers for EaTube Watch Later integration.
"""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def clean_youtube_url(url: str) -> str:
    """
    Strip Watch Later tracking params from YouTube URLs.
    
    Input:  https://www.youtube.com/watch?v=7wtfhZwyrcc&list=WL&index=1&pp=iAQBsAgC
    Output: https://www.youtube.com/watch?v=7wtfhZwyrcc
    """
    if not url:
        return url
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # Keep only the video ID parameter
        if "v" not in params:
            return url
        clean_query = urlencode({"v": params["v"][0]})
        return urlunparse(parsed._replace(query=clean_query))
    except Exception:
        return url


def get_thumbnail_url(video_id: str, quality: str = "hqdefault") -> str:
    """
    Generate YouTube thumbnail URL from video ID.
    Quality options: default, mqdefault, hqdefault, sddefault, maxresdefault
    """
    return f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"


def parse_duration_string(duration_str: str) -> int:
    """
    Convert duration string to seconds.
    Handles: "3:37" → 217, "1:08:25" → 4105, "0:33" → 33
    Used for smart playlist videos that don't have durationSeconds.
    """
    if not duration_str or not isinstance(duration_str, str):
        return 0
    try:
        duration_str = duration_str.replace(",", "").strip()
        parts = duration_str.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 1:
            return int(parts[0])
    except (ValueError, IndexError):
        pass
    return 0


def parse_formatted_duration_to_seconds(formatted: str) -> int:
    """
    Convert playlist total duration string to seconds.
    E.g. "1:29:08" → 5348, "36:34" → 2194
    Alias for parse_duration_string for clarity.
    """
    return parse_duration_string(formatted)
