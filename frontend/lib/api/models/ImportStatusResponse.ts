/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ImportStatusResponse = {
    task_id: string;
    status: string;
    total_videos: number;
    imported: number;
    failed: number;
    skipped_duplicates: number;
    progress_percentage: number;
    current_video: (string | null);
    error: (string | null);
};

