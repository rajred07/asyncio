/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PlaylistResponse = {
    id: number;
    title: string;
    description: (string | null);
    thumbnail: (string | null);
    is_public: boolean;
    owner_id: number;
    owner_username?: (string | null);
    video_count?: number;
    created_at: string;
    updated_at: (string | null);
    category?: (string | null);
    scenario?: (string | null);
    vibes?: (Array<string> | null);
    hook_description?: (string | null);
    likes_count?: number;
    saves_count?: number;
    views_count?: number;
    total_duration?: number;
    is_featured?: boolean;
    is_liked_by_me?: boolean;
    is_saved_by_me?: boolean;
};

