/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MemberRole } from './MemberRole';
export type GroupMemberResponse = {
    id: number;
    group_playlist_id: number;
    user_id: number;
    role: MemberRole;
    joined_at: string;
    username: string;
    full_name: (string | null);
    profile_image: (string | null);
};

