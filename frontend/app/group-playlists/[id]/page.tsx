'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { Users, UserPlus, Play, Trophy, Shield, Music, Video, Plus, Link as LinkIcon, Pencil, Check, X } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import toast from 'react-hot-toast';

export default function GroupPlaylistDetailPage() {
    const params = useParams();
    const playlistId = parseInt(params.id as string);
    const { user: authUser } = useAuth();
    const queryClient = useQueryClient();

    // Edit state
    const [isEditing, setIsEditing] = useState(false);
    const [editTitle, setEditTitle] = useState('');
    const [editDesc, setEditDesc] = useState('');

    // Local UI state
    const [inviteUsername, setInviteUsername] = useState('');
    const [youtubeUrl, setYoutubeUrl] = useState('');

    // API Hooks (Mocks for layout structure)
    const { data: playlist, isLoading: loadingPlaylist } = useQuery({
        queryKey: ['group-playlist', playlistId],
        queryFn: () => GroupPlaylistsService.getGroupPlaylistApiGroupPlaylistsPlaylistIdGet(playlistId),
    });

    const { data: members, isLoading: loadingMembers } = useQuery({
        queryKey: ['group-members', playlistId],
        queryFn: () => GroupPlaylistsService.getMembersApiGroupPlaylistsPlaylistIdMembersGet(playlistId),
    });

    const { data: videos, isLoading: loadingVideos } = useQuery({
        queryKey: ['group-videos', playlistId],
        queryFn: () => GroupPlaylistsService.getVideosApiGroupPlaylistsPlaylistIdVideosGet(playlistId),
    });

    const updatePlaylist = useMutation({
        mutationFn: (data: { title: string; description: string }) =>
            GroupPlaylistsService.updateGroupPlaylistApiGroupPlaylistsPlaylistIdPatch(playlistId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-playlist', playlistId] });
            toast.success('Group updated!');
            setIsEditing(false);
        },
        onError: () => toast.error('Failed to update group'),
    });

    const myRole = (members as any[])?.find((m: any) => m.user_id === authUser?.id)?.role;
    const canEdit = myRole === 'owner' || myRole === 'admin';

    const startEdit = () => {
        setEditTitle((playlist as any)?.title || '');
        setEditDesc((playlist as any)?.description || '');
        setIsEditing(true);
    };

    if (loadingPlaylist || !playlist) {
        return <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">Loading collaborative space...</div>;
    }

    return (
        <ProtectedRoute>
            <div className="flex flex-col min-h-screen bg-gray-950">
                <Navbar />
                <div className="flex-1 text-white flex flex-col md:flex-row min-h-[calc(100vh-64px)]">

                    {/* ─── LEFT PANE: SOCIAL & MEMBERS (30%) ─── */}
                    <aside className="w-full md:w-80 lg:w-96 bg-gray-900 border-r border-gray-800 flex flex-col md:h-[calc(100vh-64px)] md:sticky md:top-[64px] z-10 shrink-0">
                        <div className="p-6 border-b border-gray-800">
                            <h2 className="text-xl font-bold flex items-center gap-2 mb-2">
                                <Users size={20} className="text-blue-400" />
                                Collaboration Room
                            </h2>
                            <p className="text-sm text-gray-400">Manage members, roles, and invite friends to join.</p>
                        </div>

                        {/* Invite Section */}
                        <div className="p-6 border-b border-gray-800 bg-gray-800/30">
                            <div className="flex flex-col gap-3">
                                <label className="text-sm font-medium text-gray-300">Invite new member</label>
                                <div className="flex gap-2">
                                    <div className="relative flex-1">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <span className="text-gray-500">@</span>
                                        </div>
                                        <input
                                            type="text"
                                            value={inviteUsername}
                                            onChange={(e) => setInviteUsername(e.target.value)}
                                            placeholder="username"
                                            className="w-full pl-8 pr-3 py-2 bg-gray-950 border border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
                                        />
                                    </div>
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition"
                                    >
                                        <UserPlus size={18} />
                                    </motion.button>
                                </div>
                            </div>
                        </div>

                        {/* Members List */}
                        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
                            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Members ({members?.length || 0})</h3>
                            <div className="flex flex-col gap-4">
                                {loadingMembers ? (
                                    <p className="text-sm text-gray-500">Loading members...</p>
                                ) : members?.map((member) => (
                                    <div key={member.user_id} className="flex items-center justify-between group p-2 -mx-2 rounded-lg hover:bg-gray-800/50 transition">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-800 border border-gray-700 relative">
                                                {member.profile_image ? (
                                                    <img src={member.profile_image} alt={member.username} className="w-full h-full object-cover" />
                                                ) : (
                                                    <div className="w-full h-full flex items-center justify-center text-lg font-bold">
                                                        {member.username[0].toUpperCase()}
                                                    </div>
                                                )}
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-white flex items-center gap-1.5">
                                                    {member.username} {authUser?.id === member.user_id && <span className="text-xs bg-gray-800 px-1.5 py-0.5 rounded text-gray-400 ml-1">You</span>}
                                                </p>
                                                <p className="text-xs text-gray-500 capitalize flex items-center gap-1">
                                                    {member.role === 'owner' && <Trophy size={11} className="text-yellow-500" />}
                                                    {member.role === 'admin' && <Shield size={11} className="text-gray-400" />}
                                                    {member.role}
                                                </p>
                                            </div>
                                        </div>
                                        {/* Role management placeholder - visible on hover for owners/admins */}
                                        <button className="opacity-0 group-hover:opacity-100 text-xs text-blue-400 hover:text-blue-300 transition px-2 py-1 bg-blue-900/20 rounded">
                                            Manage
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </aside>

                    {/* ─── RIGHT PANE: CONTENT & VIDEOS (70%) ─── */}
                    <main className="flex-1 flex flex-col md:h-[calc(100vh-64px)]">

                        {/* Header Banner */}
                        <div className="relative p-8 md:p-12 overflow-hidden shrink-0 border-b border-gray-800">
                            {/* Background blurred cover */}
                            <div className="absolute inset-0 z-0">
                                {playlist.thumbnail ? (
                                    <img src={playlist.thumbnail} alt="" className="w-full h-full object-cover blur-3xl opacity-20 scale-110" />
                                ) : (
                                    <div className="w-full h-full bg-gradient-to-br from-indigo-900/40 via-purple-900/20 to-gray-900 absolute inset-0"></div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/80 to-transparent"></div>
                            </div>

                            <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start md:items-end h-full">
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                    className="w-40 h-40 md:w-56 md:h-56 shrink-0 rounded-2xl overflow-hidden shadow-2xl bg-gray-900 border border-gray-800"
                                >
                                    {playlist.thumbnail ? (
                                        <img src={playlist.thumbnail} alt={playlist.title} className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-gray-800 text-4xl">
                                            <Music className="text-gray-600 opacity-50" size={64} />
                                        </div>
                                    )}
                                </motion.div>

                                <div className="flex-1">
                                    <motion.span
                                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
                                        className="text-xs font-bold tracking-[0.2em] text-gray-400 uppercase mb-2 block"
                                    >
                                        Group Playlist
                                    </motion.span>

                                    {isEditing ? (
                                        // ── Inline Edit Form ──
                                        <div className="flex flex-col gap-3 max-w-lg">
                                            <input
                                                value={editTitle}
                                                onChange={(e) => setEditTitle(e.target.value)}
                                                className="bg-gray-800 border border-gray-600 rounded-xl px-4 py-2 text-2xl font-black text-white focus:outline-none focus:border-purple-500"
                                                placeholder="Group name..."
                                            />
                                            <textarea
                                                value={editDesc}
                                                onChange={(e) => setEditDesc(e.target.value)}
                                                rows={2}
                                                className="bg-gray-800 border border-gray-600 rounded-xl px-4 py-2 text-sm text-gray-300 focus:outline-none focus:border-purple-500 resize-none"
                                                placeholder="Description (optional)"
                                            />
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => updatePlaylist.mutate({ title: editTitle, description: editDesc })}
                                                    disabled={!editTitle.trim() || updatePlaylist.isPending}
                                                    className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                                                >
                                                    <Check size={14} /> Save
                                                </button>
                                                <button
                                                    onClick={() => setIsEditing(false)}
                                                    className="flex items-center gap-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded-lg text-sm font-semibold transition"
                                                >
                                                    <X size={14} /> Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        // ── Display Mode ──
                                        <div className="flex items-start gap-3">
                                            <div>
                                                <motion.h1
                                                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                                                    className="text-4xl md:text-6xl font-black text-white mb-4 line-clamp-2"
                                                >
                                                    {playlist.title}
                                                </motion.h1>
                                                <motion.p
                                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
                                                    className="text-gray-400 text-sm md:text-base max-w-2xl"
                                                >
                                                    {playlist.description || "A collaborative playlist space."}
                                                </motion.p>
                                            </div>
                                            {canEdit && (
                                                <button
                                                    onClick={startEdit}
                                                    className="mt-2 p-2 text-gray-500 hover:text-white hover:bg-gray-700 rounded-lg transition shrink-0"
                                                    title="Edit group name & description"
                                                >
                                                    <Pencil size={16} />
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Add Video Bar */}
                        <div className="bg-gray-900/80 backdrop-blur-xl border-b border-gray-800 p-4 sticky top-0 z-20">
                            <div className="max-w-4xl mx-auto flex gap-3">
                                <div className="relative flex-1">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <LinkIcon size={16} className="text-gray-500" />
                                    </div>
                                    <input
                                        type="text"
                                        value={youtubeUrl}
                                        onChange={(e) => setYoutubeUrl(e.target.value)}
                                        placeholder="Paste YouTube URL to add to the group..."
                                        className="w-full pl-10 pr-4 py-3 bg-gray-950 border border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-white shadow-inner"
                                    />
                                </div>
                                <motion.button
                                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                    className="bg-white text-black font-semibold px-6 py-3 rounded-xl flex items-center gap-2 transition hover:bg-gray-200 shadow-xl"
                                >
                                    <Plus size={18} />
                                    Add Video
                                </motion.button>
                            </div>
                        </div>

                        {/* Videos Feed List */}
                        <div className="flex-1 overflow-y-auto p-4 md:p-8">
                            <div className="max-w-4xl mx-auto">
                                {loadingVideos ? (
                                    <div className="space-y-4">
                                        {[1, 2, 3].map(i => (
                                            <div key={i} className="h-24 bg-gray-900 rounded-xl animate-pulse border border-gray-800"></div>
                                        ))}
                                    </div>
                                ) : videos?.length === 0 ? (
                                    <div className="text-center py-20 border-2 border-dashed border-gray-800 rounded-2xl bg-gray-900/30">
                                        <Video size={48} className="mx-auto text-gray-700 mb-4" />
                                        <h3 className="text-xl font-medium text-white mb-2">It's quiet in here</h3>
                                        <p className="text-gray-400 max-w-sm mx-auto">
                                            Paste a YouTube link above to add the first video to this group playlist!
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {videos?.map((video, index) => (
                                            <div key={video.id} className="flex gap-4 p-3 bg-gray-900/50 hover:bg-gray-800 rounded-xl border border-transparent hover:border-gray-700 transition group">
                                                <div className="w-12 flex items-center justify-center text-gray-500 font-medium group-hover:text-white transition">
                                                    {index + 1}
                                                </div>
                                                <div className="w-40 aspect-video rounded-lg overflow-hidden shrink-0 bg-gray-800 relative">
                                                    {video.thumbnail && <img src={video.thumbnail} alt="" className="w-full h-full object-cover" />}
                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition cursor-pointer">
                                                        <Play className="text-white drop-shadow-lg" size={32} />
                                                    </div>
                                                </div>
                                                <div className="flex-1 flex flex-col justify-center min-w-0">
                                                    <h4 className="font-medium text-white line-clamp-1 mb-1">{video.title}</h4>
                                                    <p className="text-sm text-gray-400">Added by @{video.added_by_username || 'unknown'}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                    </main>
                </div>
            </div>
        </ProtectedRoute>
    );
}
