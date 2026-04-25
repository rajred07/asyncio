/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InviteStatus } from './InviteStatus';
export type GroupInviteResponse = {
    id: number;
    group_playlist_id: number;
    inviter_id: number;
    invitee_id: number;
    status: InviteStatus;
    created_at: string;
    expires_at: (string | null);
    responded_at: (string | null);
    group_playlist_title: string;
    inviter_username: string;
    invitee_username: string;
};

