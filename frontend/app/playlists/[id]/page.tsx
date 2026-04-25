'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
    usePlaylist,
    usePlaylistVideos,
    useAddVideo,
    useImportPlaylist,
    useUpdateVideo,
    useDeleteVideo,
    useDeletePlaylist,
    useLikePlaylist,
    useSavePlaylist
} from '@/lib/hooks/usePlaylists';
import { VideoResponse } from '@/lib/api/models/VideoResponse';
import { useRouter } from 'next/navigation';
import {
    ArrowLeft, Play, Globe, Lock, Plus, Trash2, ExternalLink,
    Loader2, ListMusic, Youtube, Edit2, Save, X, ArrowUp, ArrowDown,
    Heart, Bookmark, Hash, Gamepad2, Film, Eye
} from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { Navbar } from '@/components/Navbar';
import { CATEGORY_GAMING } from '@/lib/constants';
import { useAuth } from '@/context/AuthContext';

export default function PlaylistDetail({ params }: { params: { id: string } }) {
    const router = useRouter();
    const playlistId = parseInt(params.id);
    const { user } = useAuth();

    // React Query Hooks
    const { data: playlist, isLoading: isPlaylistLoading, error: playlistError } = usePlaylist(playlistId);
    const { data: videos = [], isLoading: isVideosLoading } = usePlaylistVideos(playlistId);

    // Mutations
    const addVideoMutation = useAddVideo(playlistId);
    const importPlaylistMutation = useImportPlaylist(playlistId);
    const updateVideoMutation = useUpdateVideo(playlistId);
    const deleteVideoMutation = useDeleteVideo(playlistId);
    const deletePlaylistMutation = useDeletePlaylist();
    const likePlaylistMutation = useLikePlaylist();
    const savePlaylistMutation = useSavePlaylist();

    const isLoading = isPlaylistLoading || isVideosLoading;
    const error = playlistError ? 'Failed to load playlist' : null;

    // ── View tracking: fire-and-forget on mount once playlist is loaded
    useEffect(() => {
        if (!playlist) return;
        import('@/lib/api/services/PlaylistsService').then(({ PlaylistsService }) => {
            PlaylistsService.recordPlaylistViewApiPlaylistsPlaylistIdViewPost(playlistId).catch(() => { /* silent */ });
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [playlist?.id]);

    // Add Video / Import State
    const [activeTab, setActiveTab] = useState<'single' | 'import'>('single');
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [playlistUrl, setPlaylistUrl] = useState('');

    // Editing State
    const [editingVideoId, setEditingVideoId] = useState<number | null>(null);
    const [editNote, setEditNote] = useState('');

    const handleAddVideo = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!youtubeUrl.trim()) return;

        addVideoMutation.mutate(youtubeUrl, {
            onSuccess: () => setYoutubeUrl(''),
        });
    };

    const handleImportPlaylist = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!playlistUrl.trim()) return;

        const toastId = toast.loading('Importing playlist...');

        importPlaylistMutation.mutate(playlistUrl, {
            onSuccess: () => {
                setPlaylistUrl('');
                toast.dismiss(toastId);
            },
            onError: () => {
                toast.dismiss(toastId);
            }
        });
    };

    const handleDeleteVideo = async (videoId: number) => {
        if (!confirm("Are you sure you want to remove this video?")) return;
        deleteVideoMutation.mutate(videoId);
    };

    const handleDeletePlaylist = async () => {
        if (!confirm("Are you sure you want to delete this ENTIRE playlist? This cannot be undone.")) return;
        deletePlaylistMutation.mutate(playlistId);
    };

    const handleLike = () => {
        likePlaylistMutation.mutate(playlistId);
    };

    const handleSave = () => {
        savePlaylistMutation.mutate(playlistId);
    };

    const startEditing = (video: VideoResponse) => {
        if (!isOwner) return;
        setEditingVideoId(video.id);
        setEditNote(video.user_description || '');
    };

    const cancelEditing = () => {
        setEditingVideoId(null);
        setEditNote('');
    };

    const saveNote = (videoId: number) => {
        updateVideoMutation.mutate({ videoId, data: { user_description: editNote } });
        setEditingVideoId(null);
    };

    const moveVideo = (index: number, direction: 'up' | 'down') => {
        if (direction === 'up' && index === 0) return;
        if (direction === 'down' && index === videos.length - 1) return;

        const currentVideo = videos[index];
        const targetVideo = videos[direction === 'up' ? index - 1 : index + 1];

        // Optimistic swapped positions
        const newCurrentPos = targetVideo.position;
        const newTargetPos = currentVideo.position;

        updateVideoMutation.mutate({ videoId: currentVideo.id, data: { position: newCurrentPos } });
        updateVideoMutation.mutate({ videoId: targetVideo.id, data: { position: newTargetPos } });
    };

    if (isLoading) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen flex items-center justify-center text-white" style={{ background: '#0f111a' }}>
                    <Loader2 className="animate-spin text-blue-500" size={48} />
                </div>
            </ProtectedRoute>
        );
    }

    if (error || !playlist) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen p-8 text-white" style={{ background: '#0f111a' }}>
                    <div className="max-w-4xl mx-auto text-center">
                        <h1 className="text-2xl font-bold text-red-400 mb-4">Error</h1>
                        <p className="text-gray-400 mb-6">{error || 'Playlist not found'}</p>
                        <Link href="/" className="text-indigo-400 hover:text-indigo-300">
                            Return to Dashboard
                        </Link>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    const isGaming = playlist.category === CATEGORY_GAMING;
    const isOwner = user?.id === playlist.owner_id;

    return (
        <ProtectedRoute>
            <div className="min-h-screen text-white" style={{ background: '#0f111a' }}>
                <Navbar />

                <div className="max-w-6xl mx-auto p-6 md:p-8">
                    <div className="flex justify-between items-start mb-6">
                        <Link href="/" className="inline-flex items-center text-gray-400 hover:text-white transition">
                            <ArrowLeft size={20} className="mr-2" />
                            Back to Library
                        </Link>

                        {isOwner && (
                            <button
                                onClick={handleDeletePlaylist}
                                className="flex items-center gap-2 text-red-400 hover:text-red-300 hover:bg-red-400/10 px-3 py-1.5 rounded transition"
                            >
                                <Trash2 size={16} />
                                <span>Delete Playlist</span>
                            </button>
                        )}
                    </div>

                    {/* Playlist Header */}
                    <div className="flex flex-col md:flex-row gap-8 mb-12">
                        {/* Thumbnail */}
                        <div className="w-full md:w-80 aspect-video rounded-lg overflow-hidden shrink-0 relative group shadow-lg" style={{ background: '#1e2336' }}>
                            {playlist.thumbnail ? (
                                <img
                                    src={playlist.thumbnail}
                                    alt={playlist.title}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-gray-600">
                                    <ListMusic size={64} className="opacity-50" />
                                </div>
                            )}
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                <Play size={48} className="text-white fill-white" />
                            </div>
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-3xl md:text-4xl font-bold">{playlist.title}</h1>
                                {playlist.is_public ? (
                                    <Globe size={20} className="text-gray-400" />
                                ) : (
                                    <Lock size={20} className="text-gray-400" />
                                )}
                            </div>

                            {/* Tags */}
                            {(playlist.category || playlist.scenario || (playlist.vibes && playlist.vibes.length > 0)) && (
                                <div className="flex flex-wrap gap-2 mb-4">
                                    {playlist.category && (
                                        <span className="text-xs font-bold px-2 py-1 rounded-full border flex items-center gap-1 uppercase tracking-wide text-gray-300" style={{ background: '#1e2336', borderColor: '#2e3550' }}>
                                            {isGaming ? <Gamepad2 size={12} className="text-purple-400" /> : <Film size={12} className="text-pink-400" />}
                                            {playlist.category}
                                        </span>
                                    )}
                                    {playlist.scenario && (
                                        <span className="text-xs px-2 py-1 rounded-full border text-gray-400" style={{ background: '#1e2336', borderColor: '#2e3550' }}>
                                            {playlist.scenario}
                                        </span>
                                    )}
                                    {playlist.vibes?.map(vibe => (
                                        <span key={vibe} className="text-xs px-2 py-1 rounded-full border text-gray-400 flex items-center gap-1" style={{ background: '#1e2336', borderColor: '#2e3550' }}>
                                            <Hash size={10} />
                                            {vibe}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {playlist.hook_description && (
                                <p className="text-indigo-300 italic text-lg mb-3 border-l-4 border-indigo-500 pl-3">
                                    "{playlist.hook_description}"
                                </p>
                            )}

                            {playlist.description && (
                                <p className="text-gray-300 mb-6 leading-relaxed max-w-2xl">{playlist.description}</p>
                            )}

                            <div className="flex items-center justify-between border-t pt-6" style={{ borderColor: '#1e2336' }}>
                                <div className="flex items-center gap-4 text-sm text-gray-400">
                                    <span>{playlist.video_count} videos</span>
                                    <span>•</span>
                                    <span>
                                        Created by{' '}
                                        {playlist.owner_username ? (
                                            <Link href={`/user/${playlist.owner_username}`} className="text-white hover:text-indigo-400 transition font-medium">
                                                {playlist.owner_username}
                                            </Link>
                                        ) : (
                                            'Unknown'
                                        )}
                                    </span>
                                    <span>•</span>
                                    <span>{new Date(playlist.created_at).toLocaleDateString()}</span>
                                    {playlist.likes_count !== undefined && (
                                        <>
                                            <span>•</span>
                                            <span className="flex items-center gap-1 text-gray-300">
                                                <Heart size={14} className={playlist.is_liked_by_me ? "fill-red-500 text-red-500" : ""} />
                                                {playlist.likes_count} likes
                                            </span>
                                        </>
                                    )}
                                    {playlist.views_count !== undefined && (
                                        <>
                                            <span>•</span>
                                            <span className="flex items-center gap-1 text-gray-300">
                                                <Eye size={14} className="text-gray-400" />
                                                {playlist.views_count} views
                                            </span>
                                        </>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex items-center gap-3">
                                    {/* Like/Save Buttons (only for others' playlists usually, but here checking public) */}
                                    {(playlist.is_public || !isOwner) && (
                                        <>
                                            <button
                                                onClick={handleLike}
                                                className={`p-2 rounded-full transition ${playlist.is_liked_by_me ? 'bg-red-500/10 text-red-500' : 'text-gray-400 hover:text-white'}`}
                                                style={!playlist.is_liked_by_me ? { background: '#1e2336' } : {}}
                                                title={playlist.is_liked_by_me ? "Unlike" : "Like"}
                                            >
                                                <Heart size={20} className={playlist.is_liked_by_me ? "fill-current" : ""} />
                                            </button>
                                            <button
                                                onClick={handleSave}
                                                className={`p-2 rounded-full transition ${playlist.is_saved_by_me ? 'bg-indigo-500/10 text-indigo-400' : 'text-gray-400 hover:text-white'}`}
                                                style={!playlist.is_saved_by_me ? { background: '#1e2336' } : {}}
                                                title={playlist.is_saved_by_me ? "Unsave" : "Save"}
                                            >
                                                <Bookmark size={20} className={playlist.is_saved_by_me ? "fill-current" : ""} />
                                            </button>
                                        </>
                                    )}

                                    <button className="bg-white text-black hover:bg-gray-200 px-6 py-2 rounded-full font-bold flex items-center gap-2 transition shadow-md hover:shadow-lg transform active:scale-95 duration-200">
                                        <Play size={18} className="fill-black" />
                                        Play All
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Add Video Section - Only for Owner */}
                    {isOwner && (
                        <div className="rounded-xl p-6 mb-8" style={{ background: '#1e2336', border: '1px solid #252a3d' }}>
                            <div className="flex gap-4 mb-4 pb-2" style={{ borderBottom: '1px solid #252a3d' }}>
                                <button
                                    onClick={() => setActiveTab('single')}
                                    className={`pb-2 px-2 text-sm font-medium transition relative ${activeTab === 'single' ? 'text-indigo-400' : 'text-gray-400 hover:text-white'}`}
                                >
                                    Add Single Video
                                    {activeTab === 'single' && <div className="absolute bottom-[-9px] left-0 right-0 h-0.5 bg-indigo-400" />}
                                </button>
                                <button
                                    onClick={() => setActiveTab('import')}
                                    className={`pb-2 px-2 text-sm font-medium transition relative ${activeTab === 'import' ? 'text-indigo-400' : 'text-gray-400 hover:text-white'}`}
                                >
                                    Import YouTube Playlist
                                    {activeTab === 'import' && <div className="absolute bottom-[-9px] left-0 right-0 h-0.5 bg-indigo-400" />}
                                </button>
                            </div>

                            {activeTab === 'single' ? (
                                <form onSubmit={handleAddVideo} className="flex gap-4">
                                    <div className="relative flex-1">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <Youtube className="text-gray-500" size={20} />
                                        </div>
                                        <input
                                            type="text"
                                            value={youtubeUrl}
                                            onChange={(e) => setYoutubeUrl(e.target.value)}
                                            placeholder="Paste YouTube video URL here..."
                                            className="w-full border rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                            style={{ background: '#0f111a', borderColor: '#2e3550' }}
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={addVideoMutation.isPending || !youtubeUrl}
                                    className="text-white px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                        style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                                    >
                                        {addVideoMutation.isPending ? <Loader2 className="animate-spin" size={20} /> : <Plus size={20} />}
                                        Add Video
                                    </button>
                                </form>
                            ) : (
                                <form onSubmit={handleImportPlaylist} className="flex gap-4">
                                    <div className="relative flex-1">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <ListMusic className="text-gray-500" size={20} />
                                        </div>
                                        <input
                                            type="text"
                                            value={playlistUrl}
                                            onChange={(e) => setPlaylistUrl(e.target.value)}
                                            placeholder="Paste YouTube Playlist URL here..."
                                            className="w-full border rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                            style={{ background: '#0f111a', borderColor: '#2e3550' }}
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={importPlaylistMutation.isPending || !playlistUrl}
                                    className="text-white px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                        style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)' }}
                                    >
                                        {importPlaylistMutation.isPending ? <Loader2 className="animate-spin" size={20} /> : <ExternalLink size={20} />}
                                        Import
                                    </button>
                                </form>
                            )}
                        </div>
                    )}

                    {/* Videos List */}
                    <div className="space-y-4">
                        {videos.length === 0 ? (
                            <div className="text-center py-12 text-gray-500 bg-gray-800/30 rounded-xl border border-gray-800 border-dashed">
                                <p className="text-lg">No videos yet.</p>
                                {isOwner && <p className="text-sm">Add a video above to get started!</p>}
                            </div>
                        ) : (
                            videos.map((video, index) => (
                                <div
                                    key={video.id}
                                className="rounded-xl p-4 flex gap-4 transition group border hover:border-[#2e3550]"
                                    style={{ background: '#1e2336', borderColor: '#252a3d' }}
                                >
                                    {/* Video Thumbnail */}
                                    <div className="w-48 aspect-video rounded-lg overflow-hidden shrink-0 relative" style={{ background: '#0f111a' }}>
                                        <img
                                            src={video.thumbnail || ''} // Fallback to empty string if null, though backend should provide it
                                            alt={video.title}
                                            className="w-full h-full object-cover"
                                        />
                                        <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-1.5 py-0.5 rounded">
                                            {/* Duration placeholder if available, otherwise missing from model */}
                                            Video
                                        </div>
                                    </div>

                                    {/* Video Details */}
                                    <div className="flex-1 flex flex-col justify-between">
                                        <div>
                                            <a
                                                href={`https://www.youtube.com/watch?v=${video.youtube_id}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-lg font-semibold text-white hover:text-indigo-400 transition line-clamp-2 leading-tight mb-1"
                                            >
                                                {video.title}
                                            </a>
                                            <p className="text-gray-400 text-sm line-clamp-1">{video.channel_name}</p>
                                        </div>

                                        {/* Notes Section */}
                                        <div className="mt-3">
                                            {editingVideoId === video.id ? (
                                                <div className="flex gap-2 items-start">
                                                    <textarea
                                                        value={editNote}
                                                        onChange={(e) => setEditNote(e.target.value)}
                                                        className="flex-1 border rounded p-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
                                                        style={{ background: '#0f111a', borderColor: '#2e3550' }}
                                                        rows={2}
                                                        placeholder="Add a personal note..."
                                                    />
                                                    <div className="flex flex-col gap-1">
                                                        <button
                                                            onClick={() => saveNote(video.id)}
                                                            className="p-1.5 rounded text-white"
                                                                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                                                        >
                                                            <Save size={14} />
                                                        </button>
                                                        <button
                                                            onClick={cancelEditing}
                                                            className="p-1.5 rounded text-gray-300"
                                                                style={{ background: '#252a3d' }}
                                                        >
                                                            <X size={14} />
                                                        </button>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div
                                                    onClick={() => startEditing(video)}
                                                    className={`group/note ${isOwner ? 'cursor-pointer' : ''}`}
                                                >
                                                    {video.user_description ? (
                                                        <p className={`text-gray-300 text-sm italic border-l-2 pl-3 py-1 ${isOwner ? 'hover:border-indigo-500 transition' : ''}`}
                                                            style={{ borderColor: '#2e3550' }}>
                                                            {video.user_description}
                                                        </p>
                                                    ) : (
                                                        isOwner && (
                                                            <p className="text-gray-600 text-sm flex items-center gap-1 group-hover/note:text-indigo-400 transition">
                                                                <Edit2 size={12} />
                                                                Add a note...
                                                            </p>
                                                        )
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Actions - Only for Owner */}
                                    {isOwner && (
                                        <div className="flex flex-col justify-between items-end pl-4" style={{ borderLeft: '1px solid rgba(30,35,54,0.5)' }}>
                                            <div className="flex flex-col gap-1">
                                                <button
                                                    onClick={() => moveVideo(index, 'up')}
                                                    disabled={index === 0}
                                                    className="p-1.5 text-gray-500 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:hover:bg-transparent"
                                                >
                                                    <ArrowUp size={16} />
                                                </button>
                                                <button
                                                    onClick={() => moveVideo(index, 'down')}
                                                    disabled={index === videos.length - 1}
                                                    className="p-1.5 text-gray-500 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:hover:bg-transparent"
                                                >
                                                    <ArrowDown size={16} />
                                                </button>
                                            </div>
                                            <button
                                                onClick={() => handleDeleteVideo(video.id)}
                                                className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded transition"
                                                title="Remove Video"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
