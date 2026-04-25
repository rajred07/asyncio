export const CATEGORY_GAMING = "Gaming";
export const CATEGORY_ENTERTAINMENT = "Entertainment";
export const CATEGORY_EDUCATION = "Education";
export const CATEGORY_MUSIC = "Music";

export const VALID_CATEGORIES = [CATEGORY_GAMING, CATEGORY_ENTERTAINMENT, CATEGORY_EDUCATION, CATEGORY_MUSIC] as const;

// Universal Scenarios
export const SCENARIO_MEAL_TIME = "Meal Time";
export const SCENARIO_SLEEP = "Sleep/Background";
export const SCENARIO_QUICK = "Quick Dopamine";

// Gaming-specific Scenarios
export const SCENARIO_GRIND = "The Grind";
export const SCENARIO_FOCUS = "High Focus";

// Entertainment-specific Scenarios
export const SCENARIO_BINGE = "Binge Session";
export const SCENARIO_DEEP_DIVE = "Deep Dive";

// Education-specific Scenarios
export const SCENARIO_STUDY = "Study Session";
export const SCENARIO_LEARNING = "Active Learning";

// Music-specific Scenarios
export const SCENARIO_WORKOUT = "Workout";
export const SCENARIO_CHILL = "Chill Vibes";
export const SCENARIO_PARTY = "Party/Upbeat";

export const SCENARIOS_UNIVERSAL = [
    SCENARIO_MEAL_TIME,
    SCENARIO_SLEEP,
    SCENARIO_QUICK
];

export const SCENARIOS_GAMING = [
    ...SCENARIOS_UNIVERSAL,
    SCENARIO_GRIND,
    SCENARIO_FOCUS
];

export const SCENARIOS_ENTERTAINMENT = [
    ...SCENARIOS_UNIVERSAL,
    SCENARIO_BINGE,
    SCENARIO_DEEP_DIVE
];

export const SCENARIOS_EDUCATION = [
    ...SCENARIOS_UNIVERSAL,
    SCENARIO_STUDY,
    SCENARIO_LEARNING,
    SCENARIO_DEEP_DIVE
];

export const SCENARIOS_MUSIC = [
    SCENARIO_WORKOUT,
    SCENARIO_CHILL,
    SCENARIO_PARTY,
    SCENARIO_FOCUS,
    SCENARIO_SLEEP
];

// Gaming Vibes
export const VIBE_COMPETITIVE = "Competitive";
export const VIBE_LETS_PLAY = "Let's Play";
export const VIBE_SPEEDRUN = "Speedrun";
export const VIBE_LORE = "Lore/Theory";
export const VIBE_TUTORIAL = "Tutorial/Guide";
export const VIBE_FUNNY = "Funny/Memes";

export const VIBES_GAMING = [
    VIBE_COMPETITIVE,
    VIBE_LETS_PLAY,
    VIBE_SPEEDRUN,
    VIBE_LORE,
    VIBE_TUTORIAL,
    VIBE_FUNNY
];

// Entertainment Vibes
export const VIBE_COMEDY = "Comedy/Skits";
export const VIBE_COMMENTARY = "Commentary/Review";
export const VIBE_ESSAY = "Video Essay";
export const VIBE_VLOG = "Vlog/Lifestyle";
export const VIBE_HORROR = "Horror/Mystery";
export const VIBE_PODCAST = "Podcast/Talk";

export const VIBES_ENTERTAINMENT = [
    VIBE_COMEDY,
    VIBE_COMMENTARY,
    VIBE_ESSAY,
    VIBE_VLOG,
    VIBE_HORROR,
    VIBE_PODCAST
];

// Education Vibes
export const VIBE_TECH = "Tech/Coding";
export const VIBE_SCIENCE = "Science/Math";
export const VIBE_HISTORY = "History/Culture";
export const VIBE_FINANCE = "Finance/Business";
export const VIBE_HOW_TO = "How-To/DIY";

export const VIBES_EDUCATION = [
    VIBE_TECH,
    VIBE_SCIENCE,
    VIBE_HISTORY,
    VIBE_FINANCE,
    VIBE_HOW_TO,
    VIBE_PODCAST,
    VIBE_ESSAY
];

// Music Vibes
export const VIBE_LOFI = "Lo-Fi/Beats";
export const VIBE_POP = "Pop/Hits";
export const VIBE_INSTRUMENTAL = "Instrumental";
export const VIBE_ROCK = "Rock/Alternative";
export const VIBE_ACOUSTIC = "Acoustic/Live";
export const VIBE_ELECTRONIC = "Electronic/Dance";

export const VIBES_MUSIC = [
    VIBE_LOFI,
    VIBE_POP,
    VIBE_INSTRUMENTAL,
    VIBE_ROCK,
    VIBE_ACOUSTIC,
    VIBE_ELECTRONIC
];

export const getValidScenarios = (category: string) => {
    if (category === CATEGORY_GAMING) return SCENARIOS_GAMING;
    if (category === CATEGORY_ENTERTAINMENT) return SCENARIOS_ENTERTAINMENT;
    if (category === CATEGORY_EDUCATION) return SCENARIOS_EDUCATION;
    if (category === CATEGORY_MUSIC) return SCENARIOS_MUSIC;
    return [];
};

export const getValidVibes = (category: string) => {
    if (category === CATEGORY_GAMING) return VIBES_GAMING;
    if (category === CATEGORY_ENTERTAINMENT) return VIBES_ENTERTAINMENT;
    if (category === CATEGORY_EDUCATION) return VIBES_EDUCATION;
    if (category === CATEGORY_MUSIC) return VIBES_MUSIC;
    return [];
};
