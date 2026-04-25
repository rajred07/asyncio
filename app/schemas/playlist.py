from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from constant import (
    VALID_CATEGORIES,
    get_valid_scenarios,
    get_valid_vibes,
)


class PlaylistCreate(BaseModel):
    title:            str  = Field(..., min_length=1, max_length=200)
    description:      Optional[str]  = None
    thumbnail:        Optional[str]  = None
    is_public:        bool = True

    # Tag system (all optional)
    category:         Optional[str]       = None
    scenario:         Optional[str]       = None
    vibes:            Optional[List[str]] = None
    hook_description: Optional[str]       = Field(None, max_length=140)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v, info):
        if v is not None:
            category = info.data.get("category")
            if category is None:
                raise ValueError("Provide 'category' alongside 'scenario'")
            valid = get_valid_scenarios(category)
            if v not in valid:
                raise ValueError(
                    f"Invalid scenario for {category}. Valid options: {', '.join(valid)}"
                )
        return v

    @field_validator("vibes")
    @classmethod
    def validate_vibes(cls, v, info):
        if v is not None:
            if len(v) > 2:
                raise ValueError("Maximum 2 vibes allowed per playlist")
            category = info.data.get("category")
            if category is None:
                raise ValueError("Provide 'category' alongside 'vibes'")
            valid = get_valid_vibes(category)
            for vibe in v:
                if vibe not in valid:
                    raise ValueError(
                        f"Invalid vibe '{vibe}' for {category}. Valid options: {', '.join(valid)}"
                    )
        return v


class PlaylistUpdate(BaseModel):
    title:            Optional[str]       = Field(None, min_length=1, max_length=200)
    description:      Optional[str]       = None
    thumbnail:        Optional[str]       = None
    is_public:        Optional[bool]      = None

    # Tag system (all optional — can update individually)
    category:         Optional[str]       = None
    scenario:         Optional[str]       = None
    vibes:            Optional[List[str]] = None
    hook_description: Optional[str]       = Field(None, max_length=140)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v

    @model_validator(mode="after")
    def validate_scenario_and_vibes(self):
        """
        Only validate scenario/vibes against category when category is also
        provided in the same update request.  This lets users update scenario
        without resending category (the existing DB value handles it).
        """
        category = self.category

        if self.scenario is not None and category is not None:
            valid = get_valid_scenarios(category)
            if self.scenario not in valid:
                raise ValueError(
                    f"Invalid scenario for {category}. Valid options: {', '.join(valid)}"
                )

        if self.vibes is not None:
            if len(self.vibes) > 2:
                raise ValueError("Maximum 2 vibes allowed per playlist")
            if category is not None:
                valid = get_valid_vibes(category)
                for vibe in self.vibes:
                    if vibe not in valid:
                        raise ValueError(
                            f"Invalid vibe '{vibe}' for {category}. Valid options: {', '.join(valid)}"
                        )

        return self


class PlaylistResponse(BaseModel):
    id:           int
    title:        str
    description:  Optional[str]
    thumbnail:    Optional[str]
    is_public:    bool
    owner_id:     int
    owner_username: Optional[str] = None
    video_count:  int = 0
    created_at:   datetime
    updated_at:   Optional[datetime]

    # Tag system
    category:         Optional[str]       = None
    scenario:         Optional[str]       = None
    vibes:            Optional[List[str]] = None
    hook_description: Optional[str]       = None

    # Cached counters
    likes_count:    int = 0
    saves_count:    int = 0
    views_count:    int = 0
    total_duration: int = 0   # in seconds

    # Editorial
    is_featured: bool = False

    # Per-request interaction flags (computed, not stored)
    is_liked_by_me: bool = False
    is_saved_by_me: bool = False

    class Config:
        from_attributes = True