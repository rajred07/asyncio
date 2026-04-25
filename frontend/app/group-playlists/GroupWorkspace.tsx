'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService, UsersService } from '@/lib/api';
import { Users, Play, Music, Video, Plus, Link as LinkIcon, Settings2, User, Loader2, Trash2, Eye, Pencil, Check, X } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { GroupMembersDrawer } from './GroupMembersDrawer';

interface Props {
    selectedGroupId: number | null;
}

export function GroupWorkspace({ selectedGroupId }: Props) {
    if (!selectedGroupId) {
        return (
            <main className="flex-1 bg-transparent hidden md:flex flex-col items-center justify-center p-8 text-center border-l flex border-[#1e2336]">
                <div className="w-24 h-24 bg-[#1e2336] rounded-full flex items-center justify-center mb-6 border border-[#1e2336] shadow-xl">
                    <Users size={40} className="text-gray-600" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Group Playlists</h2>
                <p className="text-gray-400 max-w-sm">
                    Select a collaborative workspace from the left menu to view, manage, and jam with friends!
                </p>
            </main>
        );
    }

    return <ActiveWorkspace groupId={selectedGroupId} />;
}

// Sub-component fetching the active group's data
function ActiveWorkspace({ groupId }: { groupId: number }) {
    const { data: playlist, isLoading: loadingPlaylist } = useQuery({
        queryKey: ['group-playlist', groupId],
        queryFn: () => GroupPlaylistsService.getGroupPlaylistApiGroupPlaylistsPlaylistIdGet(groupId),
    });

    const { data: videos, isLoading: loadingVideos } = useQuery({
        queryKey: ['group-videos', groupId],
        queryFn: () => GroupPlaylistsService.getVideosApiGroupPlaylistsPlaylistIdVideosGet(groupId),
    });

    const { data: currentUser } = useQuery({
        queryKey: ['current-user'],
        queryFn: () => UsersService.getCurrentUserProfileApiUsersMeGet(),
    });

    const { data: members } = useQuery({
        queryKey: ['group-members', groupId],
        queryFn: () => GroupPlaylistsService.getMembersApiGroupPlaylistsPlaylistIdMembersGet(groupId),
    });

    const currentUserMember = members?.find(m => m.user_id === currentUser?.id);
    const currentUserRole = currentUserMember?.role || (playlist?.owner_id === currentUser?.id ? 'owner' : 'member');

    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [isMembersDrawerOpen, setIsMembersDrawerOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editTitle, setEditTitle] = useState('');
    const [editDesc, setEditDesc] = useState('');
    const queryClient = useQueryClient();

    const canEdit = currentUserRole === 'owner' || currentUserRole === 'admin';

    const startEdit = () => {
        setEditTitle((playlist as any)?.title || '');
        setEditDesc((playlist as any)?.description || '');
        setIsEditing(true);
    };

    const updatePlaylist = useMutation({
        mutationFn: (data: { title: string; description: string }) =>
            GroupPlaylistsService.updateGroupPlaylistApiGroupPlaylistsPlaylistIdPatch(groupId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-playlist', groupId] });
            toast.success('Group updated!');
            setIsEditing(false);
        },
        onError: () => toast.error('Failed to update group'),
    });

    const addVideoMutation = useMutation({
        mutationFn: (url: string) => GroupPlaylistsService.addVideoFromYoutubeApiGroupPlaylistsPlaylistIdVideosYoutubePost(groupId, url),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-videos', groupId] });
            setYoutubeUrl('');
            toast.success('Video added to the workspace!');
        },
        onError: () => {
            toast.error('Failed to add video. Please ensure it is a valid YouTube link.');
        }
    });

    const deleteVideoMutation = useMutation({
        mutationFn: (videoId: number) => GroupPlaylistsService.deleteVideoApiGroupPlaylistsPlaylistIdVideosVideoIdDelete(groupId, videoId),
        onMutate: async (deletedVideoId) => {
            await queryClient.cancelQueries({ queryKey: ['group-videos', groupId] });
            const previousVideos = queryClient.getQueryData(['group-videos', groupId]);
            queryClient.setQueryData(['group-videos', groupId], (old: any) =>
                old ? old.filter((v: any) => v.id !== deletedVideoId) : []
            );
            return { previousVideos };
        },
        onError: (err, newTodo, context) => {
            queryClient.setQueryData(['group-videos', groupId], context?.previousVideos);
            toast.error('Failed to delete video');
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['group-videos', groupId] });
        }
    });

    const handleAddVideo = () => {
        if (!youtubeUrl.trim()) return;
        addVideoMutation.mutate(youtubeUrl.trim());
    };

    if (loadingPlaylist || !playlist) {
        return <div className="flex-1 flex items-center justify-center text-gray-500 border-l border-[#1e2336]">Loading workspace...</div>;
    }

    return (
        <main className="flex-1 flex bg-transparent border-l border-[#1e2336] relative overflow-hidden">
            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 h-full relative z-0">
                {/* Header Banner - Chat style top-bar */}
                <header className="h-16 px-6 border-b border-[#1e2336] bg-[#0f111a]/40 flex items-center justify-between sticky top-0 z-20 backdrop-blur-md">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                        <div className="w-10 h-10 rounded-lg overflow-hidden bg-[#1e2336] border border-[#1e2336] relative shrink-0">
                            {playlist.thumbnail ? (
                                <img src={playlist.thumbnail} alt="" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center">
                                    <Music size={16} className="text-gray-500" />
                                </div>
                            )}
                        </div>

                        {isEditing ? (
                            // ── Inline edit form ──
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                <div className="flex flex-col gap-1 flex-1 min-w-0">
                                    <input
                                        value={editTitle}
                                        onChange={(e) => setEditTitle(e.target.value)}
                                        className="bg-[#1e2336] border border-purple-500 rounded-lg px-3 py-1 text-sm font-bold text-white focus:outline-none w-full"
                                        placeholder="Group name..."
                                        autoFocus
                                    />
                                    <input
                                        value={editDesc}
                                        onChange={(e) => setEditDesc(e.target.value)}
                                        className="bg-[#1e2336] border border-[#2a3050] rounded-lg px-3 py-1 text-xs text-gray-300 focus:outline-none focus:border-purple-500 w-full"
                                        placeholder="Description (optional)"
                                    />
                                </div>
                                <div className="flex gap-1 shrink-0">
                                    <button
                                        onClick={() => updatePlaylist.mutate({ title: editTitle, description: editDesc })}
                                        disabled={!editTitle.trim() || updatePlaylist.isPending}
                                        className="p-1.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg transition"
                                        title="Save"
                                    >
                                        {updatePlaylist.isPending ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
                                    </button>
                                    <button
                                        onClick={() => setIsEditing(false)}
                                        className="p-1.5 bg-[#1e2336] hover:bg-gray-700 text-gray-400 rounded-lg transition"
                                        title="Cancel"
                                    >
                                        <X size={14} />
                                    </button>
                                </div>
                            </div>
                        ) : (
                            // ── Display mode ──
                            <div className="flex items-center gap-2 min-w-0">
                                <div className="min-w-0">
                                    <h2 className="font-bold text-white text-base leading-tight truncate">{playlist.title}</h2>
                                    <p className="text-xs text-gray-400 truncate max-w-sm">
                                        {playlist.description || "A collaborative playlist space"}
                                    </p>
                                </div>
                                {canEdit && (
                                    <button
                                        onClick={startEdit}
                                        className="p-1.5 text-gray-600 hover:text-white hover:bg-[#1e2336] rounded-lg transition shrink-0"
                                        title="Edit group name & description"
                                    >
                                        <Pencil size={14} />
                                    </button>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setIsMembersDrawerOpen(!isMembersDrawerOpen)}
                            className={`p-2 rounded-lg transition ${isMembersDrawerOpen
                                ? 'bg-purple-600/20 text-purple-400 hover:bg-purple-600/30'
                                : 'text-gray-400 hover:text-white hover:bg-[#1e2336]'
                                }`}
                            title="Manage Members"
                        >
                            <Users size={20} />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-[#1e2336] rounded-lg transition lg:hidden border border-[#1e2336]">
                            <Settings2 size={20} />
                        </button>
                    </div>
                </header>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto relative p-6">

                    {/* Videos Space Wrapper */}
                    <div className="max-w-4xl mx-auto h-full flex flex-col">
                        {/* Add Video Input Bar */}
                        <div className="bg-[#0f111a]/80 backdrop-blur-xl border border-[#1e2336] p-2 pl-4 rounded-2xl mb-6 shadow-xl sticky top-2 z-10">
                            <div className="flex gap-3 relative z-20">
                                <div className="relative flex-1 flex items-center">
                                    <LinkIcon size={18} className="text-gray-500 mr-2 shrink-0" />
                                    <input
                                        type="text"
                                        value={youtubeUrl}
                                        onChange={(e) => setYoutubeUrl(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleAddVideo()}
                                        placeholder="Paste YouTube URL to add to the group..."
                                        className="w-full py-2 bg-transparent border-none text-sm focus:outline-none focus:ring-0 text-white placeholder-gray-500"
                                        disabled={addVideoMutation.isPending}
                                    />
                                </div>
                                <motion.button
                                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                    onClick={handleAddVideo}
                                    disabled={addVideoMutation.isPending || !youtubeUrl.trim()}
                                    className="bg-purple-600 text-white font-medium px-6 py-2 rounded-xl flex items-center gap-2 transition hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shrink-0"
                                >
                                    {addVideoMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                                    Add
                                </motion.button>
                            </div>
                        </div>

                        {/* Videos Feed */}
                        <div className="flex-1">
                            {loadingVideos ? (
                                <div className="space-y-4">
                                    {[1, 2, 3].map(i => (
                                        <div key={i} className="h-20 bg-[#1e2336] rounded-2xl animate-pulse border border-[#1e2336]/50"></div>
                                    ))}
                                </div>
                            ) : videos?.length === 0 ? (
                                <div className="text-center py-20 border-2 border-dashed border-[#1e2336] rounded-3xl bg-[#1e2336]/30">
                                    <Video size={48} className="mx-auto text-gray-700 mb-4" />
                                    <h3 className="text-xl font-medium text-white mb-2">It's quiet in here</h3>
                                    <p className="text-gray-400 max-w-xs mx-auto text-sm">
                                        Paste a YouTube link above to drop the first track into this workspace!
                                    </p>
                                </div>
                            ) : (
                                <motion.div
                                    className="space-y-3 pb-8"
                                    initial="hidden"
                                    animate="visible"
                                    variants={{
                                        visible: {
                                            transition: { staggerChildren: 0.05 }
                                        }
                                    }}
                                >
                                    {videos?.map((video, index) => {
                                        const canDelete = currentUserRole === 'owner' || currentUserRole === 'admin' || video.added_by_id === currentUser?.id;

                                        // Format duration (assuming duration is in seconds if provided, but might not be in the model. If it is, format it.
                                        // Since we don't know if the backend provides duration yet, we'll gracefully handle it.)

                                        return (
                                            <motion.div
                                                key={video.id}
                                                className="flex gap-4 p-3 bg-[#1e2336]/40 hover:bg-[#1e2336]/80 rounded-2xl border border-transparent hover:border-[#1e2336] transition group items-center relative overflow-hidden"
                                                variants={{
                                                    hidden: { opacity: 0, y: 10, scale: 0.98 },
                                                    visible: { opacity: 1, y: 0, scale: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
                                                }}
                                            >
                                                <div className="w-8 shrink-0 flex items-center justify-center text-gray-600 font-medium group-hover:text-purple-400 transition text-sm">
                                                    {index + 1}
                                                </div>
                                                <a
                                                    href={`https://www.youtube.com/watch?v=${video.youtube_id}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="w-40 aspect-video rounded-xl overflow-hidden shrink-0 bg-[#1e2336] relative border border-[#1e2336] shadow-md transition-transform group-hover:scale-[1.02] block"
                                                >
                                                    {video.thumbnail && <img src={video.thumbnail} alt="" className="w-full h-full object-cover" />}
                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition cursor-pointer backdrop-blur-sm">
                                                        <Play className="text-white drop-shadow-lg" size={24} fill="currentColor" />
                                                    </div>
                                                </a>
                                                <div className="flex-1 flex flex-col justify-center min-w-0 pr-12">
                                                    <a
                                                        href={`https://www.youtube.com/watch?v=${video.youtube_id}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="font-medium text-gray-100 line-clamp-1 mb-1 group-hover:text-purple-300 transition hover:underline text-base"
                                                    >
                                                        {video.title}
                                                    </a>
                                                    <div className="text-sm text-gray-400 mb-2 truncate">
                                                        {video.channel_name}
                                                    </div>
                                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                                        <span className="flex items-center gap-1.5 bg-[#1e2336] px-2 py-1 rounded-md text-gray-300">
                                                            <User size={12} className="text-purple-400" />
                                                            {video.added_by_username || 'unknown'}
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <Eye size={12} />
                                                            {video.views ? video.views.toLocaleString() : '0'} views
                                                        </span>
                                                        {/* If there's a duration field we show it, else skip */}
                                                    </div>
                                                </div>

                                                {/* Delete Button (Conditional) */}
                                                {canDelete && (
                                                    <button
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            deleteVideoMutation.mutate(video.id);
                                                            toast.success("Removing video...");
                                                        }}
                                                        disabled={deleteVideoMutation.isPending}
                                                        className="absolute right-4 p-2 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-xl opacity-0 group-hover:opacity-100 transition disabled:opacity-50"
                                                        title="Remove Video"
                                                    >
                                                        <Trash2 size={18} />
                                                    </button>
                                                )}
                                            </motion.div>
                                        );
                                    })}
                                </motion.div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <GroupMembersDrawer
                playlistId={groupId}
                isOpen={isMembersDrawerOpen}
                onClose={() => setIsMembersDrawerOpen(false)}
                playlistOwnerId={playlist.owner_id}
                members={members || []}
                currentUserRole={currentUserRole as 'owner' | 'admin' | 'member'}
                currentUserId={currentUser?.id}
            />
        </main>
    );
}
