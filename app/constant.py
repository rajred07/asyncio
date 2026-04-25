"""
Constants for Playlist Tag System
Gaming, Entertainment, Education, and Music categories
with scenarios and vibes for smart playlist organization.
"""

# ── Main Categories ────────────────────────────────────────────────────────
CATEGORY_GAMING       = "Gaming"
CATEGORY_ENTERTAINMENT = "Entertainment"
CATEGORY_EDUCATION    = "Education"
CATEGORY_MUSIC        = "Music"

VALID_CATEGORIES = [
    CATEGORY_GAMING,
    CATEGORY_ENTERTAINMENT,
    CATEGORY_EDUCATION,
    CATEGORY_MUSIC,
]

# ── Universal Scenarios (available for all categories) ─────────────────────
SCENARIO_MEAL_TIME    = "Meal Time"
SCENARIO_SLEEP        = "Sleep/Background"
SCENARIO_QUICK        = "Quick Dopamine"

SCENARIOS_UNIVERSAL = [
    SCENARIO_MEAL_TIME,
    SCENARIO_SLEEP,
    SCENARIO_QUICK,
]

# ── Gaming-specific Scenarios ──────────────────────────────────────────────
SCENARIO_GRIND        = "The Grind"
SCENARIO_HIGH_FOCUS   = "High Focus"

SCENARIOS_GAMING = SCENARIOS_UNIVERSAL + [
    SCENARIO_GRIND,
    SCENARIO_HIGH_FOCUS,
]

# ── Entertainment-specific Scenarios ──────────────────────────────────────
SCENARIO_BINGE        = "Binge Session"
SCENARIO_DEEP_DIVE    = "Deep Dive"

SCENARIOS_ENTERTAINMENT = SCENARIOS_UNIVERSAL + [
    SCENARIO_BINGE,
    SCENARIO_DEEP_DIVE,
]

# ── Education-specific Scenarios ───────────────────────────────────────────
SCENARIO_ACTIVE_LEARNING = "Active Learning"
SCENARIO_STUDY_SESSION   = "Study Session"

SCENARIOS_EDUCATION = SCENARIOS_UNIVERSAL + [
    SCENARIO_DEEP_DIVE,          # shared with Entertainment
    SCENARIO_ACTIVE_LEARNING,
    SCENARIO_STUDY_SESSION,
]

# ── Music-specific Scenarios ───────────────────────────────────────────────
SCENARIO_WORKOUT     = "Workout"
SCENARIO_CHILL_VIBES = "Chill Vibes"
SCENARIO_COMMUTE     = "Commute"

SCENARIOS_MUSIC = SCENARIOS_UNIVERSAL + [
    SCENARIO_HIGH_FOCUS,         # shared with Gaming (coding focus)
    SCENARIO_WORKOUT,
    SCENARIO_CHILL_VIBES,
    SCENARIO_COMMUTE,
]

# ── Gaming Vibes (Sub-genres) ──────────────────────────────────────────────
VIBE_COMPETITIVE  = "Competitive"
VIBE_LETS_PLAY    = "Let's Play"
VIBE_SPEEDRUN     = "Speedrun"
VIBE_LORE         = "Lore/Theory"
VIBE_TUTORIAL     = "Tutorial/Guide"
VIBE_FUNNY        = "Funny/Memes"
VIBE_INDIE        = "Indie/Hidden Gems"
VIBE_RETRO        = "Retro/Classic"

VIBES_GAMING = [
    VIBE_COMPETITIVE,
    VIBE_LETS_PLAY,
    VIBE_SPEEDRUN,
    VIBE_LORE,
    VIBE_TUTORIAL,
    VIBE_FUNNY,
    VIBE_INDIE,
    VIBE_RETRO,
]

# ── Entertainment Vibes (Sub-genres) ──────────────────────────────────────
VIBE_COMEDY       = "Comedy/Skits"
VIBE_COMMENTARY   = "Commentary/Review"
VIBE_ESSAY        = "Video Essay"
VIBE_VLOG         = "Vlog/Lifestyle"
VIBE_HORROR       = "Horror/Mystery"
VIBE_PODCAST      = "Podcast/Talk"
VIBE_REACTION     = "Reaction/Watch-Along"
VIBE_DOCUMENTARY  = "Documentary"

VIBES_ENTERTAINMENT = [
    VIBE_COMEDY,
    VIBE_COMMENTARY,
    VIBE_ESSAY,
    VIBE_VLOG,
    VIBE_HORROR,
    VIBE_PODCAST,
    VIBE_REACTION,
    VIBE_DOCUMENTARY,
]

# ── Education Vibes (Sub-genres) ───────────────────────────────────────────
VIBE_TECH_CODING   = "Tech/Coding"
VIBE_SCIENCE_MATH  = "Science/Math"
VIBE_HISTORY       = "History/Culture"
VIBE_HOW_TO        = "How-To/DIY"
VIBE_LANGUAGE      = "Language Learning"
VIBE_FINANCE       = "Finance/Business"
VIBE_PHILOSOPHY    = "Philosophy/Critical Thinking"
VIBE_EDU_ESSAY     = "Video Essay"     # shared with Entertainment

VIBES_EDUCATION = [
    VIBE_TECH_CODING,
    VIBE_SCIENCE_MATH,
    VIBE_HISTORY,
    VIBE_HOW_TO,
    VIBE_LANGUAGE,
    VIBE_FINANCE,
    VIBE_PHILOSOPHY,
    VIBE_EDU_ESSAY,
]

# ── Music Vibes (Sub-genres) ───────────────────────────────────────────────
VIBE_LOFI         = "Lo-Fi/Beats"
VIBE_INSTRUMENTAL = "Instrumental"
VIBE_ELECTRONIC   = "Electronic/Dance"
VIBE_ROCK_ALT     = "Rock/Alternative"
VIBE_ACOUSTIC     = "Acoustic/Live"
VIBE_HIPHOP       = "Hip-Hop/R&B"
VIBE_CLASSICAL    = "Classical/Orchestral"
VIBE_INDIE_MUSIC  = "Indie/Alternative"

VIBES_MUSIC = [
    VIBE_LOFI,
    VIBE_INSTRUMENTAL,
    VIBE_ELECTRONIC,
    VIBE_ROCK_ALT,
    VIBE_ACOUSTIC,
    VIBE_HIPHOP,
    VIBE_CLASSICAL,
    VIBE_INDIE_MUSIC,
]

# ── Helper Functions ───────────────────────────────────────────────────────

def get_valid_scenarios(category: str) -> list:
    """Returns valid scenarios for a given category."""
    mapping = {
        CATEGORY_GAMING:       SCENARIOS_GAMING,
        CATEGORY_ENTERTAINMENT: SCENARIOS_ENTERTAINMENT,
        CATEGORY_EDUCATION:    SCENARIOS_EDUCATION,
        CATEGORY_MUSIC:        SCENARIOS_MUSIC,
    }
    return mapping.get(category, [])


def get_valid_vibes(category: str) -> list:
    """Returns valid vibes for a given category."""
    mapping = {
        CATEGORY_GAMING:       VIBES_GAMING,
        CATEGORY_ENTERTAINMENT: VIBES_ENTERTAINMENT,
        CATEGORY_EDUCATION:    VIBES_EDUCATION,
        CATEGORY_MUSIC:        VIBES_MUSIC,
    }
    return mapping.get(category, [])


def get_all_valid_scenarios() -> list:
    """Returns all unique scenarios across all categories (for UI dropdowns)."""
    all_scenarios = set()
    for cat in VALID_CATEGORIES:
        all_scenarios.update(get_valid_scenarios(cat))
    return sorted(all_scenarios)


def get_all_valid_vibes() -> list:
    """Returns all unique vibes across all categories (for UI dropdowns)."""
    all_vibes = set()
    for cat in VALID_CATEGORIES:
        all_vibes.update(get_valid_vibes(cat))
    return sorted(all_vibes)