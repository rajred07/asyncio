import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { PlaylistResponse } from '../models/PlaylistResponse';

// ─── Response Types ───────────────────────────────────────────────────────────

export type UserSearchResult = {
    id: number;
    username: string;
    full_name?: string | null;
    bio?: string | null;
    profile_image?: string | null;
    followers_count?: number;
    following_count?: number;
};

export type SearchResponse = {
    query: string;
    playlists: PlaylistResponse[];
    users: UserSearchResult[];
    playlists_count: number;
    users_count: number;
};

// ─── Service ──────────────────────────────────────────────────────────────────

export class SearchService {
    /**
     * Unified Global Search
     * Returns up to 10 playlists (FTS + engagement ranked) and up to 5 users.
     * @param q         Search query (min 2 chars)
     * @param type      all | playlists | users
     */
    public static search(
        q: string,
        type: 'all' | 'playlists' | 'users' = 'all',
    ): CancelablePromise<SearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/search',
            query: { q, type },
            errors: {
                400: `Query too short`,
                422: `Validation Error`,
            },
        });
    }
}
