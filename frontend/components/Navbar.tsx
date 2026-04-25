'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { LogOut, Search, Bell, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, FormEvent, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService } from '@/lib/api';
import toast from 'react-hot-toast';

export function Navbar() {
    const router = useRouter();
    const { user, logout } = useAuth();
    const [searchQuery, setSearchQuery] = useState('');
    const [inboxOpen, setInboxOpen] = useState(false);
    const inboxRef = useRef<HTMLDivElement>(null);
    const queryClient = useQueryClient();

    // Call backend to blacklist the JWT, then clear local state
    const handleLogout = async () => {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/users/logout`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                });
            }
        } catch {
            // Silently ignore — even if the API call fails, we still log the user out locally
        } finally {
            logout(); // clears localStorage + redirects (existing AuthContext logic)
        }
    };

    const handleSearch = (e: FormEvent) => {
        e.preventDefault();
        const q = searchQuery.trim();
        if (q.length < 2) return;
        router.push(`/search?q=${encodeURIComponent(q)}`);
        setSearchQuery('');
    };

    // Fetch pending invites — poll every 5 minutes (reduces server load)
    // Note: React Query auto-pauses polling when the tab is backgrounded,
    // so this does NOT fire continuously when the user is offline/inactive.
    const { data: pendingInvites = [] } = useQuery({
        queryKey: ['group-invites-pending'],
        queryFn: () => GroupPlaylistsService.getPendingInvitesApiGroupPlaylistsInvitesPendingGet(),
        refetchInterval: 5 * 60 * 1000, // 5 minutes
        refetchIntervalInBackground: false, // pause when tab is not focused
    });

    const acceptInvite = useMutation({
        mutationFn: (id: number) =>
            GroupPlaylistsService.acceptInviteApiGroupPlaylistsInvitesInviteIdAcceptPost(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-invites-pending'] });
            queryClient.invalidateQueries({ queryKey: ['my-group-playlists'] });
            toast.success('Joined the group! 🎉');
        },
        onError: () => toast.error('Failed to accept invite'),
    });

    const rejectInvite = useMutation({
        mutationFn: (id: number) =>
            GroupPlaylistsService.rejectInviteApiGroupPlaylistsInvitesInviteIdRejectPost(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-invites-pending'] });
            toast.success('Invite declined');
        },
        onError: () => toast.error('Failed to decline invite'),
    });

    // Close on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (inboxRef.current && !inboxRef.current.contains(e.target as Node)) {
                setInboxOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const inviteCount = (pendingInvites as any[]).length;

    return (
        <nav className="bg-[#0f111a] border-b border-[#1e2336] sticky top-0 z-40 h-[64px]">
            <div className="max-w-[1600px] mx-auto px-4 h-full">
                <div className="flex items-center justify-between h-full gap-4">

                    {/* Logo (Left) */}
                    <div className="flex items-center w-[200px] shrink-0">
                        <Link href="/" className="flex items-center gap-2 group">
                            <Sparkles size={20} className="text-indigo-400 group-hover:text-fuchsia-400 transition-colors" />
                            <span
                                className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent"
                                style={{ backgroundImage: 'linear-gradient(135deg, #818cf8 0%, #c084fc 100%)' }}
                            >
                                Curate
                            </span>
                        </Link>
                    </div>

                    {/* Search Bar (Center) */}
                    <form onSubmit={handleSearch} className="flex-1 max-w-[480px]">
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search size={16} className="text-gray-500" />
                            </div>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search playlists, users..."
                                className="w-full bg-[#1e2336] border border-[#2a3050] rounded-full pl-9 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/60 focus:bg-[#252a42] transition-all"
                            />
                        </div>
                    </form>

                    {/* Actions (Right) */}
                    <div className="flex items-center gap-3 w-[200px] justify-end shrink-0">

                        {/* ── Inbox Bell ── */}
                        <div className="relative" ref={inboxRef}>
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.92 }}
                                onClick={() => setInboxOpen((v) => !v)}
                                className="relative p-2 text-gray-400 hover:text-white hover:bg-[#1e2336] rounded-xl transition-colors"
                                title="Group Invites"
                            >
                                <Bell size={18} />
                                {inviteCount > 0 && (
                                    <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-purple-600 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1">
                                        {inviteCount}
                                    </span>
                                )}
                            </motion.button>

                            {/* Dropdown */}
                            <AnimatePresence>
                                {inboxOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -8, scale: 0.97 }}
                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                        exit={{ opacity: 0, y: -8, scale: 0.97 }}
                                        transition={{ duration: 0.15 }}
                                        className="absolute right-0 top-full mt-2 w-80 bg-[#13162a] border border-[#1e2336] rounded-2xl shadow-2xl overflow-hidden z-50"
                                    >
                                        <div className="p-3 border-b border-[#1e2336] flex items-center justify-between">
                                            <span className="text-sm font-semibold text-white">Group Invites</span>
                                            {inviteCount > 0 && (
                                                <span className="bg-purple-600 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                                                    {inviteCount} pending
                                                </span>
                                            )}
                                        </div>

                                        <div className="max-h-80 overflow-y-auto">
                                            {inviteCount === 0 ? (
                                                <div className="py-10 text-center text-sm text-gray-500">
                                                    No pending invites 🎉
                                                </div>
                                            ) : (
                                                <div className="p-2 space-y-2">
                                                    {(pendingInvites as any[]).map((invite) => (
                                                        <div
                                                            key={invite.id}
                                                            className="bg-[#1a1d32] rounded-xl p-3 border border-[#1e2336]"
                                                        >
                                                            <p className="text-sm font-medium text-white line-clamp-1">
                                                                {invite.group_playlist_title}
                                                            </p>
                                                            <p className="text-xs text-gray-500 mt-0.5 mb-3">
                                                                Invited by @{invite.inviter_username}
                                                            </p>
                                                            <div className="flex gap-2">
                                                                <button
                                                                    onClick={() => acceptInvite.mutate(invite.id)}
                                                                    disabled={acceptInvite.isPending}
                                                                    className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg py-1.5 text-xs font-semibold transition"
                                                                >
                                                                    ✓ Join
                                                                </button>
                                                                <button
                                                                    onClick={() => rejectInvite.mutate(invite.id)}
                                                                    disabled={rejectInvite.isPending}
                                                                    className="flex-1 bg-[#252a42] hover:bg-[#2d3350] disabled:opacity-50 text-gray-300 rounded-lg py-1.5 text-xs font-semibold transition"
                                                                >
                                                                    ✕ Decline
                                                                </button>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>

                                        <div className="p-2 border-t border-[#1e2336]">
                                            <Link
                                                href="/group-playlists"
                                                onClick={() => setInboxOpen(false)}
                                                className="block text-center text-xs text-purple-400 hover:text-purple-300 py-1 transition"
                                            >
                                                View all groups →
                                            </Link>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Username + Logout */}
                        <div className="flex items-center gap-3 flex-row-reverse text-right">
                            <Link href="/profile" className="hidden sm:block hover:opacity-80 transition-opacity">
                                <div className="text-sm font-medium text-white">
                                    {user?.username || user?.full_name}
                                </div>
                                <div className="text-xs text-gray-500">@{user?.username}</div>
                            </Link>
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.92 }}
                                onClick={handleLogout}
                                className="p-2 text-gray-400 hover:text-white hover:bg-[#1e2336] rounded-xl transition-colors"
                                title="Logout"
                            >
                                <LogOut size={18} />
                            </motion.button>
                        </div>
                    </div>

                </div>
            </div>
        </nav>
    );
}
