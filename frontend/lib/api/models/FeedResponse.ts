/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedFilters } from './FeedFilters';
import type { PlaylistResponse } from './PlaylistResponse';
/**
 * Paginated feed response with metadata
 */
export type FeedResponse = {
    playlists: Array<PlaylistResponse>;
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
    sort: string;
    filters?: (FeedFilters | null);
};

