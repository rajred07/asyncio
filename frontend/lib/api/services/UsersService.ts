/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_api_users_login_post } from '../models/Body_login_api_users_login_post';
import type { Token } from '../models/Token';
import type { UserCreate } from '../models/UserCreate';
import type { UserPublicProfile } from '../models/UserPublicProfile';
import type { UserResponse } from '../models/UserResponse';
import type { UserUpdate } from '../models/UserUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * Register User
     * Register a new user
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public static registerUserApiUsersRegisterPost(
        requestBody: UserCreate,
    ): CancelablePromise<UserResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/users/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Login
     * Login user and return JWT token (OAuth2 compatible)
     * @param formData
     * @returns Token Successful Response
     * @throws ApiError
     */
    public static loginApiUsersLoginPost(
        formData: Body_login_api_users_login_post,
    ): CancelablePromise<Token> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/users/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current User Profile
     * Get current user's profile
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public static getCurrentUserProfileApiUsersMeGet(): CancelablePromise<UserResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/users/me',
        });
    }
    /**
     * Update Current User Profile
     * Update current user's profile
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public static updateCurrentUserProfileApiUsersMePut(
        requestBody: UserUpdate,
    ): CancelablePromise<UserResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/users/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Current User
     * Delete current user's account
     * @returns void
     * @throws ApiError
     */
    public static deleteCurrentUserApiUsersMeDelete(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/users/me',
        });
    }
    /**
     * Get User By Username
     * Get user profile by username (public)
     * @param username
     * @returns UserPublicProfile Successful Response
     * @throws ApiError
     */
    public static getUserByUsernameApiUsersUsernameGet(
        username: string,
    ): CancelablePromise<UserPublicProfile> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/users/{username}',
            path: {
                'username': username,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Follow User
     * Follow a user
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static followUserApiUsersUserIdFollowPost(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/users/{user_id}/follow',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Unfollow User
     * Unfollow a user
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static unfollowUserApiUsersUserIdFollowDelete(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/users/{user_id}/follow',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Followers
     * Get all followers of a user
     * @param userId
     * @returns UserPublicProfile Successful Response
     * @throws ApiError
     */
    public static getUserFollowersApiUsersUserIdFollowersGet(
        userId: number,
    ): CancelablePromise<Array<UserPublicProfile>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/users/{user_id}/followers',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Following
     * Get all users that a user follows
     * @param userId
     * @returns UserPublicProfile Successful Response
     * @throws ApiError
     */
    public static getUserFollowingApiUsersUserIdFollowingGet(
        userId: number,
    ): CancelablePromise<Array<UserPublicProfile>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/users/{user_id}/following',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
