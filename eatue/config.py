# ============================================================
# EaTube Processing Pipeline - Configuration
# ============================================================
# Paste your API keys below before running process_watchlater.py
import os


# 1. YouTube Data API v3 Key (same one from your Chrome extension)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY_HERE")

# 2. Google Gemini API Key (free at https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")  # Get free key from https://aistudio.google.com/apikey

# ============================================================
# Processing Settings
# ============================================================

# How many videos to process (set to 10 for testing, 310 for full run)
VIDEO_LIMIT = 50

# Path to your Watch Later JSON file
WATCHLATER_PATH = "watchlater.json"

# Output file paths
ENRICHED_OUTPUT_PATH = "enriched_watchlater.json"
PLAYLISTS_OUTPUT_PATH = "playlists.json"

# Gemini model to use
GEMINI_MODEL = "gemini-2.5-flash"

# Batch sizes
YOUTUBE_API_BATCH_SIZE = 50   # YouTube API max per request
GEMINI_BATCH_SIZE = 10        # Videos per Gemini categorization call

# ============================================================
# YouTube Category ID → Name Mapping
# ============================================================
YOUTUBE_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
    "30": "Movies",
    "31": "Anime/Animation",
    "32": "Action/Adventure",
    "33": "Classics",
    "34": "Comedy",
    "35": "Documentary",
    "36": "Drama",
    "37": "Family",
    "38": "Foreign",
    "39": "Horror",
    "40": "Sci-Fi/Fantasy",
    "41": "Thriller",
    "42": "Shorts",
    "43": "Shows",
    "44": "Trailers",
}

# ============================================================
# Locked Category Schema for Gemini (tailored to YOUR content)
# ============================================================
LOCKED_CATEGORIES = [
    "Bollywood & Hindi Music",
    "Western & English Music",
    "Marathi Music & Culture",
    "Indian Classical & Devotional",
    "Gaming",
    "Comedy & Roast",
    "Entertainment & Pop Culture",
    "Food & Cooking",
    "Education & Information",
    "Sports & Cricket",
    "Health & Wellness",
    "News & Politics",
    "Movies & Superheroes",
    "Vlogs & Lifestyle",
    "Other",
]

MOOD_TAGS = [
    "Happy", "Sad", "Inspiring", "Funny", "Intense",
    "Calm", "Exciting", "Nostalgic", "Energetic", "Emotional",
]

VIEWING_TIMES = ["Morning", "Afternoon", "Evening", "Night", "Anytime"]

VIEWING_CONTEXTS = [
    "Workout", "Study", "Commute", "Relax", "Focus",
    "Background", "Social", "Cooking", "Quick Break",
]
