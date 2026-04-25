/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GroupInviteCreate } from '../models/GroupInviteCreate';
import type { GroupInviteResponse } from '../models/GroupInviteResponse';
import type { GroupMemberResponse } from '../models/GroupMemberResponse';
import type { GroupPlaylistCreate } from '../models/GroupPlaylistCreate';
import type { GroupPlaylistDetailResponse } from '../models/GroupPlaylistDetailResponse';
import type { GroupPlaylistResponse } from '../models/GroupPlaylistResponse';
import type { GroupPlaylistUpdate } from '../models/GroupPlaylistUpdate';
import type { GroupVideoCreate } from '../models/GroupVideoCreate';
import type { GroupVideoResponse } from '../models/GroupVideoResponse';
import type { ImportStatusResponse } from '../models/ImportStatusResponse';
import type { InviteActionResponse } from '../models/InviteActionResponse';
import type { PlaylistImportRequest } from '../models/PlaylistImportRequest';
import type { PlaylistImportResponse } from '../models/PlaylistImportResponse';
import type { UpdateMemberRole } from '../models/UpdateMemberRole';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GroupPlaylistsService {
    /**
     * Get My Group Playlists
     * Get all group playlists where current user is a member
     * @returns GroupPlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getMyGroupPlaylistsApiGroupPlaylistsGet(): CancelablePromise<Array<GroupPlaylistResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/',
        });
    }
    /**
     * Create Group Playlist
     * Create a new group playlist (user becomes owner)
     * @param requestBody
     * @returns GroupPlaylistResponse Successful Response
     * @throws ApiError
     */
    public static createGroupPlaylistApiGroupPlaylistsPost(
        requestBody: GroupPlaylistCreate,
    ): CancelablePromise<GroupPlaylistResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Owned Playlists
     * Get all group playlists owned by current user
     * @returns GroupPlaylistResponse Successful Response
     * @throws ApiError
     */
    public static getOwnedPlaylistsApiGroupPlaylistsOwnedGet(): CancelablePromise<Array<GroupPlaylistResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/owned',
        });
    }
    /**
     * Get Group Playlist
     * Get group playlist details
     * @param playlistId
     * @returns GroupPlaylistDetailResponse Successful Response
     * @throws ApiError
     */
    public static getGroupPlaylistApiGroupPlaylistsPlaylistIdGet(
        playlistId: number,
    ): CancelablePromise<GroupPlaylistDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/{playlist_id}',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Group Playlist
     * Update group playlist (owner/admin only)
     * @param playlistId
     * @param requestBody
     * @returns GroupPlaylistResponse Successful Response
     * @throws ApiError
     */
    public static updateGroupPlaylistApiGroupPlaylistsPlaylistIdPatch(
        playlistId: number,
        requestBody: GroupPlaylistUpdate,
    ): CancelablePromise<GroupPlaylistResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/group-playlists/{playlist_id}',
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
     * Delete Group Playlist
     * Delete group playlist (owner only)
     * @param playlistId
     * @returns void
     * @throws ApiError
     */
    public static deleteGroupPlaylistApiGroupPlaylistsPlaylistIdDelete(
        playlistId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/group-playlists/{playlist_id}',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Invite User
     * Invite a user to group playlist (owner/admin only)
     * @param playlistId
     * @param requestBody
     * @returns GroupInviteResponse Successful Response
     * @throws ApiError
     */
    public static inviteUserApiGroupPlaylistsPlaylistIdInvitePost(
        playlistId: number,
        requestBody: GroupInviteCreate,
    ): CancelablePromise<GroupInviteResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/{playlist_id}/invite',
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
     * Get Pending Invites
     * Get all pending invites for current user
     * @returns GroupInviteResponse Successful Response
     * @throws ApiError
     */
    public static getPendingInvitesApiGroupPlaylistsInvitesPendingGet(): CancelablePromise<Array<GroupInviteResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/invites/pending',
        });
    }
    /**
     * Accept Invite
     * Accept an invite
     * @param inviteId
     * @returns InviteActionResponse Successful Response
     * @throws ApiError
     */
    public static acceptInviteApiGroupPlaylistsInvitesInviteIdAcceptPost(
        inviteId: number,
    ): CancelablePromise<InviteActionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/invites/{invite_id}/accept',
            path: {
                'invite_id': inviteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reject Invite
     * Reject an invite
     * @param inviteId
     * @returns InviteActionResponse Successful Response
     * @throws ApiError
     */
    public static rejectInviteApiGroupPlaylistsInvitesInviteIdRejectPost(
        inviteId: number,
    ): CancelablePromise<InviteActionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/invites/{invite_id}/reject',
            path: {
                'invite_id': inviteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Members
     * Get all members of a group playlist
     * @param playlistId
     * @returns GroupMemberResponse Successful Response
     * @throws ApiError
     */
    public static getMembersApiGroupPlaylistsPlaylistIdMembersGet(
        playlistId: number,
    ): CancelablePromise<Array<GroupMemberResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/{playlist_id}/members',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Member Role
     * Update a member's role (owner only)
     * @param playlistId
     * @param userId
     * @param requestBody
     * @returns GroupMemberResponse Successful Response
     * @throws ApiError
     */
    public static updateMemberRoleApiGroupPlaylistsPlaylistIdMembersUserIdRolePatch(
        playlistId: number,
        userId: number,
        requestBody: UpdateMemberRole,
    ): CancelablePromise<GroupMemberResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/group-playlists/{playlist_id}/members/{user_id}/role',
            path: {
                'playlist_id': playlistId,
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Remove Member
     * Remove a member from group playlist
     * @param playlistId
     * @param userId
     * @returns void
     * @throws ApiError
     */
    public static removeMemberApiGroupPlaylistsPlaylistIdMembersUserIdDelete(
        playlistId: number,
        userId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/group-playlists/{playlist_id}/members/{user_id}',
            path: {
                'playlist_id': playlistId,
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Video From Youtube
     * Add video to group playlist from YouTube URL (all members can add)
     * @param playlistId
     * @param youtubeUrl
     * @param userDescription
     * @returns GroupVideoResponse Successful Response
     * @throws ApiError
     */
    public static addVideoFromYoutubeApiGroupPlaylistsPlaylistIdVideosYoutubePost(
        playlistId: number,
        youtubeUrl: string,
        userDescription?: string,
    ): CancelablePromise<GroupVideoResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/{playlist_id}/videos/youtube',
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
     * Add Video
     * Add a video to group playlist (all members can add)
     * @param playlistId
     * @param requestBody
     * @returns GroupVideoResponse Successful Response
     * @throws ApiError
     */
    public static addVideoApiGroupPlaylistsPlaylistIdVideosPost(
        playlistId: number,
        requestBody: GroupVideoCreate,
    ): CancelablePromise<GroupVideoResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/{playlist_id}/videos',
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
     * Get Videos
     * Get all videos in a group playlist
     * @param playlistId
     * @returns GroupVideoResponse Successful Response
     * @throws ApiError
     */
    public static getVideosApiGroupPlaylistsPlaylistIdVideosGet(
        playlistId: number,
    ): CancelablePromise<Array<GroupVideoResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/{playlist_id}/videos',
            path: {
                'playlist_id': playlistId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Video
     * Delete a video from group playlist (permission-based)
     * @param playlistId
     * @param videoId
     * @returns void
     * @throws ApiError
     */
    public static deleteVideoApiGroupPlaylistsPlaylistIdVideosVideoIdDelete(
        playlistId: number,
        videoId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/group-playlists/{playlist_id}/videos/{video_id}',
            path: {
                'playlist_id': playlistId,
                'video_id': videoId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Youtube Playlist
     * Import entire YouTube playlist (runs in background)
     * Returns immediately with task_id for progress tracking
     * @param playlistId
     * @param requestBody
     * @returns PlaylistImportResponse Successful Response
     * @throws ApiError
     */
    public static importYoutubePlaylistApiGroupPlaylistsPlaylistIdVideosImportPlaylistPost(
        playlistId: number,
        requestBody: PlaylistImportRequest,
    ): CancelablePromise<PlaylistImportResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/group-playlists/{playlist_id}/videos/import-playlist',
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
     * Get Import Status
     * Get the status of a playlist import task
     * @param taskId
     * @returns ImportStatusResponse Successful Response
     * @throws ApiError
     */
    public static getImportStatusApiGroupPlaylistsImportStatusTaskIdGet(
        taskId: string,
    ): CancelablePromise<ImportStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/group-playlists/import-status/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
