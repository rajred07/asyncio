/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedResponse } from '../models/FeedResponse';
import type { LikeResponse } from '../models/LikeResponse';
import type { PlaylistCreate } from '../models/PlaylistCreate';
import type { PlaylistResponse } from '../models/PlaylistResponse';
import type { PlaylistUpdate } from '../models/PlaylistUpdate';
import type { SaveResponse } from '../models/SaveResponse';
import type { VideoResponse } from '../models/VideoResponse';
import type { VideoUpdate } from '../models/VideoUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PlaylistsService {
    /**
     * Create Playlist
     * Create a new playlist
     * @param requestBody
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static createPlaylistApiPlaylistsPost(
        requestBody: PlaylistCreate,
    ): CancelablePromise<PlaylistResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Playlists
     * Get all playlists owned by current user
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getMyPlaylistsApiPlaylistsMyGet(): CancelablePromise<Array<PlaylistResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/my',
        });
    }
    /**
     * Get My Liked Playlists
     * Get all playlists liked by current user
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getMyLikedPlaylistsApiPlaylistsLikedGet(): CancelablePromise<Array<PlaylistResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/liked',
        });
    }
    /**
     * Get My Saved Playlists
     * Get all playlists saved by current user (user's library)
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getMySavedPlaylistsApiPlaylistsSavedGet(): CancelablePromise<Array<PlaylistResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/saved',
        });
    }
    /**
     * Get Playlist Feed
     * Get paginated feed of public playlists with filters
     *
     * Query Parameters:
     * - page: Page number (default: 1)
     * - page_size: Items per page (default: 20, max: 50)
     * - category: Filter by category (Gaming/Entertainment)
     * - scenario: Filter by scenario (Meal Time, Sleep, etc.)
     * - vibes: Filter by vibes (comma-separated: "Lore/Theory,Comedy/Skits")
     * - sort: Sort by popular/recent/trending (default: popular)
     * @param page
     * @param pageSize
     * @param category
     * @param scenario
     * @param vibes
     * @param sort
     * @returns FeedResponse Successful Response
     * @throws ApiError
     */
    public static getPlaylistFeedApiPlaylistsFeedGet(
        page: number = 1,
        pageSize: number = 20,
        category?: (string | null),
        scenario?: (string | null),
        vibes?: (string | null),
        sort: string = 'popular',
    ): CancelablePromise<FeedResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/feed',
            query: {
                'page': page,
                'page_size': pageSize,
                'category': category,
                'scenario': scenario,
                'vibes': vibes,
                'sort': sort,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * For You Feed
     * Personalized feed sorted by engagement score.
     * Playlists in the user's preferred_categories get a 1.5× boost.
     * Excludes the user's own playlists.
     * Filters: category, duration (quick/medium/long)
     * @param page
     * @param pageSize
     * @param category
     * @param duration
     * @returns any Successful Response
     * @throws ApiError
     */
    public static forYouFeedApiPlaylistsFeedForYouGet(
        page: number = 1,
        pageSize: number = 20,
        category?: (string | null),
        duration?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/feed/for-you',
            query: {
                'page': page,
                'page_size': pageSize,
                'category': category,
                'duration': duration,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Following Feed
     * Chronological playlists from users the current user follows.
     * Returns empty list + helpful message if not following anyone.
     * @param page
     * @param pageSize
     * @returns any Successful Response
     * @throws ApiError
     */
    public static followingFeedApiPlaylistsFeedFollowingGet(
        page: number = 1,
        pageSize: number = 20,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/feed/following',
            query: {
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Trending Feed
     * Playlists ranked by 24-hour rolling engagement.
     * trending_score = recent_likes×2 + recent_saves×3
     * No personalization — pure popularity signal.
     * @param page
     * @param pageSize
     * @param category
     * @returns any Successful Response
     * @throws ApiError
     */
    public static trendingFeedApiPlaylistsFeedTrendingGet(
        page: number = 1,
        pageSize: number = 20,
        category?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/feed/trending',
            query: {
                'page': page,
                'page_size': pageSize,
                'category': category,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Feed Sections
     * Returns all 4 horizontal scroll sections for the For You tab in one request:
     * - editors_picks:       is_featured playlists (admin-curated)
     * - trending_now:        top 5 by 24h engagement
     * - because_you_liked:   similar to last liked playlist
     * - new_and_rising:      < 48h old, above-average likes
     * @returns any Successful Response
     * @throws ApiError
     */
    public static feedSectionsApiPlaylistsFeedSectionsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/feed/sections',
        });
    }
    /**
     * Get Playlist
     * Get playlist by ID with user interaction flags
     * @param playlistId
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getPlaylistApiPlaylistsPlaylistIdGet(
        playlistId: number,
    ): CancelablePromise<PlaylistResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/{playlist_id}',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Playlist
     * Update playlist (owner only)
     * @param playlistId
     * @param requestBody
     * @returns PlaylistResponse Successful Response
     * @throws ApiError
     */
    public static updatePlaylistApiPlaylistsPlaylistIdPut(
        playlistId: number,
        requestBody: PlaylistUpdate,
    ): CancelablePromise<PlaylistResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/playlists/{playlist_id}',
            path: {
                'playlist_id': playlistId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Playlist
     * Delete playlist (owner only)
     * @param playlistId
     * @returns void
     * @throws ApiError
     */
    public static deletePlaylistApiPlaylistsPlaylistIdDelete(
        playlistId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/playlists/{playlist_id}',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Like Playlist
     * Toggle like on a playlist
     * @param playlistId
     * @returns LikeResponse Successful Response
     * @throws ApiError
     */
    public static likePlaylistApiPlaylistsPlaylistIdLikePost(
        playlistId: number,
    ): CancelablePromise<LikeResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/{playlist_id}/like',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Save Playlist
     * Toggle save on a playlist (add/remove from library)
     * @param playlistId
     * @returns SaveResponse Successful Response
     * @throws ApiError
     */
    public static savePlaylistApiPlaylistsPlaylistIdSavePost(
        playlistId: number,
    ): CancelablePromise<SaveResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/{playlist_id}/save',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Record Playlist View
     * Record a view on a playlist with IP-based deduplication.
     * Same IP viewing the same playlist within 1 hour counts as 1 view.
     * Come back after 1 hour → counts again.
     * @param playlistId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static recordPlaylistViewApiPlaylistsPlaylistIdViewPost(
        playlistId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/{playlist_id}/view',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Video From Youtube
     * Add video to playlist from YouTube URL (owner only)
     * @param playlistId
     * @param youtubeUrl
     * @param userDescription
     * @returns VideoResponse Successful Response
     * @throws ApiError
     */
    public static addVideoFromYoutubeApiPlaylistsPlaylistIdVideosYoutubePost(
        playlistId: number,
        youtubeUrl: string,
        userDescription?: string,
    ): CancelablePromise<VideoResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/{playlist_id}/videos/youtube',
            path: {
                'playlist_id': playlistId,
            },
            query: {
                'youtube_url': youtubeUrl,
                'user_description': userDescription,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Playlist Videos
     * Get all videos in a playlist
     * @param playlistId
     * @returns VideoResponse Successful Response
     * @throws ApiError
     */
    public static getPlaylistVideosApiPlaylistsPlaylistIdVideosGet(
        playlistId: number,
    ): CancelablePromise<Array<VideoResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/playlists/{playlist_id}/videos',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Video
     * Update video (owner only)
     * @param videoId
     * @param requestBody
     * @returns VideoResponse Successful Response
     * @throws ApiError
     */
    public static updateVideoApiPlaylistsVideosVideoIdPut(
        videoId: number,
        requestBody: VideoUpdate,
    ): CancelablePromise<VideoResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/playlists/videos/{video_id}',
            path: {
                'video_id': videoId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Video
     * Remove video from playlist (owner only)
     * @param videoId
     * @returns void
     * @throws ApiError
     */
    public static deleteVideoApiPlaylistsVideosVideoIdDelete(
        videoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/playlists/videos/{video_id}',
            path: {
                'video_id': videoId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Youtube Playlist
     * Bulk import YouTube playlist (owner only)
     * @param playlistId
     * @param youtubePlaylistUrl
     * @param maxVideos
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importYoutubePlaylistApiPlaylistsPlaylistIdVideosImportPlaylistPost(
        playlistId: number,
        youtubePlaylistUrl: string,
        maxVideos: number = 50,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/playlists/{playlist_id}/videos/import-playlist',
            path: {
                'playlist_id': playlistId,
            },
            query: {
                'youtube_playlist_url': youtubePlaylistUrl,
                'max_videos': maxVideos,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
