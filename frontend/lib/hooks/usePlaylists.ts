import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PlaylistsService } from '@/lib/api/services/PlaylistsService';
import { PlaylistCreate } from '@/lib/api/models/PlaylistCreate';
import { VideoUpdate } from '@/lib/api/models/VideoUpdate';
import { PlaylistUpdate } from '@/lib/api/models/PlaylistUpdate';
import { PlaylistResponse } from '@/lib/api/models/PlaylistResponse';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

export const PLAYLISTS_KEYS = {
    all: ['playlists'] as const,
    my: () => [...PLAYLISTS_KEYS.all, 'my'] as const,
    detail: (id: number) => [...PLAYLISTS_KEYS.all, id] as const,
    videos: (id: number) => [...PLAYLISTS_KEYS.detail(id), 'videos'] as const,
};

// --- QUERIES ---

export function useMyPlaylists() {
    return useQuery({
        queryKey: PLAYLISTS_KEYS.my(),
        queryFn: () => PlaylistsService.getMyPlaylistsApiPlaylistsMyGet(),
    });
}

export function usePlaylist(id: number) {
    return useQuery({
        queryKey: PLAYLISTS_KEYS.detail(id),
        queryFn: () => PlaylistsService.getPlaylistApiPlaylistsPlaylistIdGet(id),
        enabled: !!id,
    });
}

export function usePlaylistVideos(id: number) {
    return useQuery({
        queryKey: PLAYLISTS_KEYS.videos(id),
        queryFn: async () => {
            const videos = await PlaylistsService.getPlaylistVideosApiPlaylistsPlaylistIdVideosGet(id);
            return videos.sort((a, b) => a.position - b.position);
        },
        enabled: !!id,
    });
}

// --- MUTATIONS ---

export function useCreatePlaylist() {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: (data: PlaylistCreate) => PlaylistsService.createPlaylistApiPlaylistsPost(data),
        onSuccess: (newPlaylist) => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.my() });
            toast.success('Playlist Created!');
            router.push(`/playlists/${newPlaylist.id}`);
        },
        onError: (error) => {
            console.error('Create playlist error:', error);
            toast.error('Failed to create playlist');
        },
    });
}

export function useImportPlaylist(playlistId: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (youtubePlaylistUrl: string) =>
            PlaylistsService.importYoutubePlaylistApiPlaylistsPlaylistIdVideosImportPlaylistPost(playlistId, youtubePlaylistUrl),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.videos(playlistId) });
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.detail(playlistId) }); // Update count
            toast.success('Import Complete!');
        },
        onError: (error) => {
            console.error('Import playlist error:', error);
            toast.error('Failed to import playlist');
        },
    });
}

export function useAddVideo(playlistId: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (youtubeUrl: string) =>
            PlaylistsService.addVideoFromYoutubeApiPlaylistsPlaylistIdVideosYoutubePost(playlistId, youtubeUrl),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.videos(playlistId) });
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.detail(playlistId) }); // Update count
            toast.success('Video Added!');
        },
        onError: (error) => {
            console.error('Add video error:', error);
            toast.error('Failed to add video');
        },
    });
}

export function useUpdateVideo(playlistId: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ videoId, data }: { videoId: number; data: VideoUpdate }) =>
            PlaylistsService.updateVideoApiPlaylistsVideosVideoIdPut(videoId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.videos(playlistId) });
            // Optimistic updates could be added here for even faster feel
        },
        onError: (error) => {
            console.error('Update video error:', error);
            toast.error('Failed to save changes');
        },
    });
}

export function useDeleteVideo(playlistId: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (videoId: number) =>
            PlaylistsService.deleteVideoApiPlaylistsVideosVideoIdDelete(videoId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.videos(playlistId) });
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.detail(playlistId) }); // Update count
            toast.success('Video Deleted');
        },
        onError: (error) => {
            console.error('Delete video error:', error);
            toast.error('Failed to delete video');
        },
    });
}

// --- QUERIES (Updated) ---

export function useLikedPlaylists() {
    return useQuery({
        queryKey: [...PLAYLISTS_KEYS.all, 'liked'],
        queryFn: () => PlaylistsService.getMyLikedPlaylistsApiPlaylistsLikedGet(),
    });
}

export function useSavedPlaylists() {
    return useQuery({
        queryKey: [...PLAYLISTS_KEYS.all, 'saved'],
        queryFn: () => PlaylistsService.getMySavedPlaylistsApiPlaylistsSavedGet(),
    });
}

// --- MUTATIONS (Updated) ---

export function useUpdatePlaylist(playlistId: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: PlaylistUpdate) =>
            PlaylistsService.updatePlaylistApiPlaylistsPlaylistIdPut(playlistId, data),
        onSuccess: (updatedPlaylist) => {
            queryClient.setQueryData(PLAYLISTS_KEYS.detail(playlistId), updatedPlaylist);
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.my() });
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.all }); // Refresh feeds/lists
            toast.success('Playlist Updated');
        },
        onError: (error) => {
            console.error('Update playlist error:', error);
            toast.error('Failed to update playlist');
        },
    });
}

export function useLikePlaylist() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (playlistId: number) =>
            PlaylistsService.likePlaylistApiPlaylistsPlaylistIdLikePost(playlistId),
        onSuccess: (data, playlistId) => {
            // Optimistically update the playlist detail
            queryClient.setQueryData(PLAYLISTS_KEYS.detail(playlistId), (old: PlaylistResponse | undefined) => {
                if (!old) return old;
                return {
                    ...old,
                    is_liked_by_me: data.liked,
                    likes_count: data.likes_count
                };
            });
            // Also invalidate to be sure
            queryClient.invalidateQueries({ queryKey: [...PLAYLISTS_KEYS.all, 'liked'] });

            toast.success(data.liked ? 'Liked!' : 'Unliked');
        },
        onError: (error) => {
            console.error('Like playlist error:', error);
            toast.error('Failed to like playlist');
        },
    });
}

export function useSavePlaylist() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (playlistId: number) =>
            PlaylistsService.savePlaylistApiPlaylistsPlaylistIdSavePost(playlistId),
        onSuccess: (data, playlistId) => {
            // Optimistically update
            queryClient.setQueryData(PLAYLISTS_KEYS.detail(playlistId), (old: PlaylistResponse | undefined) => {
                if (!old) return old;
                return {
                    ...old,
                    is_saved_by_me: data.saved
                };
            });
            queryClient.invalidateQueries({ queryKey: [...PLAYLISTS_KEYS.all, 'saved'] });

            toast.success(data.saved ? 'Saved to Library' : 'Removed from Library');
        },
        onError: (error) => {
            console.error('Save playlist error:', error);
            toast.error('Failed to save playlist');
        },
    });
}

export function useDeletePlaylist() {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: (playlistId: number) =>
            PlaylistsService.deletePlaylistApiPlaylistsPlaylistIdDelete(playlistId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PLAYLISTS_KEYS.my() });
            toast.success('Playlist Deleted');
            router.push('/');
        },
        onError: (error) => {
            console.error('Delete playlist error:', error);
            toast.error('Failed to delete playlist');
        },
    });
}

