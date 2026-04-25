'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useSearch } from '@/lib/hooks/useSearch';
import { Navbar } from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import Link from 'next/link';
import {
    Search, Loader2, ListMusic, Users, Heart, Eye,
    Bookmark, Hash, Gamepad2, Film, UserCircle
} from 'lucide-react';
import { PlaylistResponse } from '@/lib/api/models/PlaylistResponse';
import { UserSearchResult } from '@/lib/api/services/SearchService';
import { useSavePlaylist } from '@/lib/hooks/usePlaylists';
import toast from 'react-hot-toast';

// ─── Playlist Card ──────────────────────────────────────────────────────────

function PlaylistCard({ playlist }: { playlist: PlaylistResponse }) {
    const saveMutation = useSavePlaylist();

    const handleSave = (e: React.MouseEvent) => {
        e.preventDefault();
        saveMutation.mutate(playlist.id, {
            onSuccess: (data: any) => toast.success(data?.saved ? 'Saved!' : 'Removed from library'),
        });
    };

    return (
        <Link
            href={`/playlists/${playlist.id}`}
            className="group flex gap-4 bg-[#141726] border border-[#1e2336] rounded-xl p-4 hover:border-blue-500/40 hover:bg-[#181d30] transition-all duration-200"
        >
            {/* Thumbnail */}
            <div className="w-32 aspect-video shrink-0 rounded-lg overflow-hidden bg-gray-800 relative">
                {playlist.thumbnail ? (
                    <img
                        src={playlist.thumbnail}
                        alt={playlist.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center">
                        <ListMusic size={28} className="text-gray-600" />
                    </div>
                )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white text-sm leading-tight line-clamp-2 group-hover:text-blue-300 transition-colors">
                    {playlist.title}
                </h3>

                {/* Creator */}
                {playlist.owner_username && (
                    <p className="text-xs text-gray-500 mt-0.5">
                        by{' '}
                        <span className="text-gray-400 hover:text-white transition-colors">
                            @{playlist.owner_username}
                        </span>
                    </p>
                )}

                {/* Tags */}
                {(playlist.category || (playlist.vibes && playlist.vibes.length > 0)) && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                        {playlist.category && (
                            <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 bg-[#1e2336] text-gray-400 rounded-full border border-[#2a3050]">
                                {playlist.category === 'Gaming'
                                    ? <Gamepad2 size={9} className="text-purple-400" />
                                    : <Film size={9} className="text-pink-400" />}
                                {playlist.category}
                            </span>
                        )}
                        {playlist.vibes?.slice(0, 2).map((vibe) => (
                            <span key={vibe} className="flex items-center gap-1 text-[10px] px-2 py-0.5 bg-[#1e2336] text-gray-500 rounded-full border border-[#2a3050]">
                                <Hash size={8} />
                                {vibe}
                            </span>
                        ))}
                    </div>
                )}

                {/* Stats */}
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    {playlist.likes_count !== undefined && (
                        <span className="flex items-center gap-1">
                            <Heart size={11} className={playlist.is_liked_by_me ? 'fill-red-500 text-red-500' : ''} />
                            {playlist.likes_count}
                        </span>
                    )}
                    {playlist.views_count !== undefined && (
                        <span className="flex items-center gap-1">
                            <Eye size={11} />
                            {playlist.views_count}
                        </span>
                    )}
                    {playlist.video_count !== undefined && (
                        <span className="flex items-center gap-1">
                            <ListMusic size={11} />
                            {playlist.video_count} videos
                        </span>
                    )}
                </div>
            </div>

            {/* Save button */}
            <button
                onClick={handleSave}
                className={`self-start p-1.5 rounded-lg transition-colors ${playlist.is_saved_by_me
                    ? 'text-blue-400 bg-blue-400/10'
                    : 'text-gray-600 hover:text-gray-300 hover:bg-[#1e2336]'
                    }`}
                title={playlist.is_saved_by_me ? 'Remove from library' : 'Save to library'}
            >
                <Bookmark size={15} className={playlist.is_saved_by_me ? 'fill-current' : ''} />
            </button>
        </Link>
    );
}

// ─── User Card ──────────────────────────────────────────────────────────────

function UserCard({ user }: { user: UserSearchResult }) {
    return (
        <Link
            href={`/user/${user.username}`}
            className="flex items-center gap-3 bg-[#141726] border border-[#1e2336] rounded-xl px-4 py-3 hover:border-blue-500/40 hover:bg-[#181d30] transition-all duration-200 group"
        >
            {/* Avatar */}
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0 overflow-hidden">
                {user.profile_image ? (
                    <img src={user.profile_image} alt={user.username} className="w-full h-full object-cover" />
                ) : (
                    <UserCircle size={24} className="text-white" />
                )}
            </div>

            {/* Info */}
            <div className="min-w-0 flex-1">
                <p className="font-semibold text-white text-sm group-hover:text-blue-300 transition-colors">
                    {user.username}
                </p>
                {user.full_name && (
                    <p className="text-xs text-gray-500 truncate">{user.full_name}</p>
                )}
            </div>

            {/* Followers */}
            <div className="text-right shrink-0">
                <p className="text-xs text-gray-400 font-medium flex items-center gap-1">
                    <Users size={11} />
                    {user.followers_count ?? 0}
                </p>
                <p className="text-[10px] text-gray-600">followers</p>
            </div>
        </Link>
    );
}

// ─── Search Content (uses useSearchParams, must be in Suspense) ─────────────

function SearchContent() {
    const searchParams = useSearchParams();
    const q = searchParams.get('q') ?? '';
    const [type, setType] = useState<'all' | 'playlists' | 'users'>('all');

    const { data, isLoading, isError } = useSearch(q, type);

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            {/* Header */}
            <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
                <div>
                    {q ? (
                        <>
                            <p className="text-xs text-gray-500 uppercase tracking-widest font-medium mb-1">Search results for</p>
                            <h1 className="text-2xl font-bold text-white">"{q}"</h1>
                        </>
                    ) : (
                        <h1 className="text-2xl font-bold text-white">Search</h1>
                    )}
                </div>

                {/* Type filter */}
                <div className="flex gap-1 bg-[#141726] border border-[#1e2336] rounded-xl p-1">
                    {(['all', 'playlists', 'users'] as const).map((t) => (
                        <button
                            key={t}
                            onClick={() => setType(t)}
                            className={`px-4 py-1.5 text-sm rounded-lg capitalize font-medium transition-all ${type === t
                                ? 'bg-blue-600 text-white shadow'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            {/* Empty state — no query */}
            {!q && (
                <div className="text-center py-24">
                    <Search size={48} className="mx-auto text-gray-600 mb-4" />
                    <p className="text-gray-400 text-lg font-medium">Start typing to search</p>
                    <p className="text-gray-600 text-sm mt-1">Find playlists and creators</p>
                </div>
            )}

            {/* Loading */}
            {q && isLoading && (
                <div className="flex justify-center py-24">
                    <Loader2 size={36} className="animate-spin text-blue-500" />
                </div>
            )}

            {/* Error */}
            {q && isError && (
                <div className="text-center py-16">
                    <p className="text-red-400">Something went wrong. Please try again.</p>
                </div>
            )}

            {/* Results */}
            {q && data && !isLoading && (
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-8">

                    {/* Playlists Column */}
                    {type !== 'users' && (
                        <div>
                            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <ListMusic size={13} />
                                Playlists
                                {data.playlists_count > 0 && (
                                    <span className="bg-blue-600/20 text-blue-400 text-[10px] px-2 py-0.5 rounded-full font-bold">
                                        {data.playlists_count}
                                    </span>
                                )}
                            </h2>

                            {data.playlists.length === 0 ? (
                                <div className="text-center py-16 border border-dashed border-[#1e2336] rounded-xl">
                                    <ListMusic size={32} className="mx-auto text-gray-700 mb-3" />
                                    <p className="text-gray-500">No playlists found for "{q}"</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {data.playlists.map((p) => (
                                        <PlaylistCard key={p.id} playlist={p} />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Users Column */}
                    {type !== 'playlists' && (
                        <div>
                            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <Users size={13} />
                                Users
                                {data.users_count > 0 && (
                                    <span className="bg-purple-600/20 text-purple-400 text-[10px] px-2 py-0.5 rounded-full font-bold">
                                        {data.users_count}
                                    </span>
                                )}
                            </h2>

                            {data.users.length === 0 ? (
                                <div className="text-center py-16 border border-dashed border-[#1e2336] rounded-xl">
                                    <Users size={32} className="mx-auto text-gray-700 mb-3" />
                                    <p className="text-gray-500">No users found for "{q}"</p>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    {data.users.map((u) => (
                                        <UserCard key={u.id} user={u} />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                </div>
            )}
        </div>
    );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function SearchPage() {
    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-[#0a0b14] text-white">
                <Navbar />
                <Suspense fallback={
                    <div className="flex justify-center py-32">
                        <Loader2 size={36} className="animate-spin text-blue-500" />
                    </div>
                }>
                    <SearchContent />
                </Suspense>
            </div>
        </ProtectedRoute>
    );
}
