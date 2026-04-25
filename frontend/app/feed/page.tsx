'use client';

import { useState, useEffect, useRef } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Navbar } from '@/components/Navbar';
import { PlaylistCard } from '@/components/PlaylistCard';
import { PlaylistsService } from '@/lib/api/services/PlaylistsService';
import { useQuery } from '@tanstack/react-query';
import { Filter, RefreshCw, Flame, Users, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { VALID_CATEGORIES } from '@/lib/constants';
import { motion, AnimatePresence } from 'framer-motion';
import { PlaylistResponse } from '@/lib/api/models/PlaylistResponse';
import Link from 'next/link';

// ─── Types ───────────────────────────────────────────────────────────────────

type FeedTab = 'for-you' | 'following' | 'trending';

const TABS: { id: FeedTab; label: string; icon: React.ElementType }[] = [
    { id: 'for-you', label: 'For You', icon: Sparkles },
    { id: 'following', label: 'Following', icon: Users },
    { id: 'trending', label: 'Trending', icon: Flame },
];

const DURATION_OPTIONS = [
    { value: '', label: 'Any length' },
    { value: 'quick', label: '⚡ Quick (< 30 min)' },
    { value: 'medium', label: '🎯 Medium (30–90 min)' },
    { value: 'long', label: '🎬 Long (> 90 min)' },
];

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function SkeletonCard() {
    return (
        <div className="rounded-lg overflow-hidden border animate-pulse shrink-0 w-52" style={{ background: '#1e2336', borderColor: '#2a3050' }}>
            <div className="aspect-video" style={{ background: '#252a42' }} />
            <div className="p-3 space-y-2">
                <div className="h-3 rounded w-3/4" style={{ background: '#252a42' }} />
                <div className="h-2 rounded w-1/2" style={{ background: '#252a42' }} />
            </div>
        </div>
    );
}

function SkeletonGrid() {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="rounded-lg overflow-hidden border animate-pulse" style={{ background: '#1e2336', borderColor: '#2a3050' }}>
                    <div className="aspect-video" style={{ background: '#252a42' }} />
                    <div className="p-4 space-y-3">
                        <div className="h-4 rounded w-3/4" style={{ background: '#252a42' }} />
                        <div className="h-3 rounded w-1/2" style={{ background: '#252a42' }} />
                        <div className="h-3 rounded w-1/3" style={{ background: '#252a42' }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

// ─── Horizontal scroll row ────────────────────────────────────────────────────

function SectionRow({ title, playlists, emoji }: { title: string; playlists: PlaylistResponse[]; emoji: string }) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const scroll = (dir: 'left' | 'right') => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({ left: dir === 'left' ? -320 : 320, behavior: 'smooth' });
        }
    };

    if (!playlists || !Array.isArray(playlists) || playlists.length === 0) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mb-10"
        >
            <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>{emoji}</span> {title}
                </h2>
                <div className="flex gap-1">
                    <button onClick={() => scroll('left')} className="p-1.5 rounded-lg text-gray-400 hover:text-white transition" style={{ background: '#1e2336' }}>
                        <ChevronLeft size={18} />
                    </button>
                    <button onClick={() => scroll('right')} className="p-1.5 rounded-lg text-gray-400 hover:text-white transition" style={{ background: '#1e2336' }}>
                        <ChevronRight size={18} />
                    </button>
                </div>
            </div>
            <div
                ref={scrollRef}
                className="flex gap-4 overflow-x-auto pb-6 pt-2 scrollbar-hide items-stretch"
                style={{ scrollbarWidth: 'none' }}
            >
                {playlists.map((pl, i) => (
                    <motion.div
                        key={pl.id}
                        initial={{ opacity: 0, scale: 0.9, x: 20 }}
                        animate={{ opacity: 1, scale: 1, x: 0 }}
                        transition={{ delay: i * 0.05, duration: 0.4, type: "spring", stiffness: 200, damping: 20 }}
                        className="shrink-0 w-64 sm:w-72 flex flex-col"
                    >
                        <PlaylistCard playlist={pl} />
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
}

// ─── Stagger grid variants ────────────────────────────────────────────────────

const gridVariants = { hidden: {}, show: { transition: { staggerChildren: 0.12 } } } as const;
const cardVariants = { hidden: { opacity: 0, y: 22 }, show: { opacity: 1, y: 0 } } as const;

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function FeedPage() {
    const [activeTab, setActiveTab] = useState<FeedTab>('for-you');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedDuration, setSelectedDuration] = useState('');
    const [page, setPage] = useState(1);

    // Reset page + filters on tab change
    useEffect(() => { setPage(1); setSelectedCategory(''); setSelectedDuration(''); }, [activeTab]);
    useEffect(() => { setPage(1); }, [selectedCategory, selectedDuration]);

    // ─ Queries ─
    const sectionsQuery = useQuery({
        queryKey: ['feed-sections'],
        queryFn: () => PlaylistsService.feedSectionsApiPlaylistsFeedSectionsGet(),
        staleTime: 5 * 60 * 1000, // 5 min
        enabled: activeTab === 'for-you',
    });

    const forYouQuery = useQuery({
        queryKey: ['feed-for-you', page, selectedCategory, selectedDuration],
        queryFn: () => PlaylistsService.forYouFeedApiPlaylistsFeedForYouGet(page, 20, selectedCategory || undefined, selectedDuration || undefined),
        placeholderData: (prev) => prev,
        enabled: activeTab === 'for-you',
    });

    const followingQuery = useQuery({
        queryKey: ['feed-following', page],
        queryFn: () => PlaylistsService.followingFeedApiPlaylistsFeedFollowingGet(page, 20),
        placeholderData: (prev) => prev,
        enabled: activeTab === 'following',
    });

    const trendingQuery = useQuery({
        queryKey: ['feed-trending', page, selectedCategory],
        queryFn: () => PlaylistsService.trendingFeedApiPlaylistsFeedTrendingGet(page, 20, selectedCategory || undefined),
        placeholderData: (prev) => prev,
        enabled: activeTab === 'trending',
    });

    // Active query for current tab
    const activeQuery =
        activeTab === 'for-you' ? forYouQuery :
            activeTab === 'following' ? followingQuery :
                trendingQuery;

    const playlists: PlaylistResponse[] = activeQuery.data?.playlists ?? [];
    // Backend returns { total, page, page_size } — compute pagination ourselves
    const total: number = activeQuery.data?.total ?? 0;
    const currentPageSize: number = activeQuery.data?.page_size ?? 20;
    const totalPages: number = total > 0 ? Math.ceil(total / currentPageSize) : 1;
    const hasNext: boolean = page < totalPages;

    // Sections data
    const sections = sectionsQuery.data;

    return (
        <ProtectedRoute>
            <div className="min-h-screen text-white" style={{ background: '#0f111a' }}>
                <Navbar />

                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

                    {/* ─── Header ─────────────────────────────────── */}
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        className="mb-6"
                    >
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent" style={{ backgroundImage: 'linear-gradient(90deg, #818cf8, #a78bfa)' }}>
                            Discover
                        </h1>
                        <p className="text-gray-400 text-sm mt-1">Explore playlists from the community</p>
                    </motion.div>

                    {/* ─── 3-Tab Switcher ──────────────────────────── */}
                    <div className="flex p-1 rounded-xl self-start mb-8 w-fit border" style={{ background: '#1e2336', borderColor: '#2a3050' }}>
                        {TABS.map(({ id, label, icon: Icon }) => (
                            <button
                                key={id}
                                onClick={() => setActiveTab(id)}
                                className={`relative flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors z-10 ${activeTab === id ? 'text-white' : 'text-gray-500 hover:text-gray-200'
                                    }`}
                            >
                                {activeTab === id && (
                                    <motion.span
                                        layoutId="feed-tab-pill"
                                        className="absolute inset-0 rounded-lg shadow"
                                        style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3))', border: '1px solid rgba(99,102,241,0.4)' }}
                                        transition={{ type: 'spring', stiffness: 380, damping: 32 }}
                                    />
                                )}
                                <span className="relative z-10 flex items-center gap-2">
                                    <Icon size={16} />
                                    {label}
                                </span>
                            </button>
                        ))}
                    </div>

                    {/* ─── Filters (For You + Trending tabs) ──────── */}
                    <AnimatePresence mode="wait">
                        {(activeTab === 'for-you' || activeTab === 'trending') && (
                            <motion.div
                                key={`filters-${activeTab}`}
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -4 }}
                                transition={{ duration: 0.2 }}
                                className="rounded-xl p-4 mb-8 border shadow-lg"
                                style={{ background: '#1e2336', borderColor: '#2a3050' }}
                            >
                                <div className="flex flex-wrap gap-4 items-center">
                                    <div className="flex items-center gap-2 text-gray-400">
                                        <Filter size={16} />
                                        <span className="text-sm font-medium">Filters:</span>
                                    </div>

                                    <select
                                        value={selectedCategory}
                                        onChange={(e) => setSelectedCategory(e.target.value)}
                                        className="border rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2"
                                        style={{ background: '#252a42', borderColor: '#2a3050' }}
                                    >
                                        <option value="">All Categories</option>
                                        {VALID_CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                                    </select>

                                    {activeTab === 'for-you' && (
                                        <select
                                            value={selectedDuration}
                                            onChange={(e) => setSelectedDuration(e.target.value)}
                                            className="border rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2"
                                            style={{ background: '#252a42', borderColor: '#2a3050' }}
                                        >
                                            {DURATION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                                        </select>
                                    )}

                                    <motion.button
                                        whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                                        onClick={() => { setSelectedCategory(''); setSelectedDuration(''); }}
                                        className="ml-auto text-sm flex items-center gap-1"
                                        style={{ color: '#818cf8' }}
                                    >
                                        <RefreshCw size={14} /> Reset
                                    </motion.button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* ─── For You: Sections horizontal rows ──────── */}
                    <AnimatePresence mode="wait">
                        {activeTab === 'for-you' && !sectionsQuery.isLoading && sections && (
                            <motion.div key="sections" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                                <SectionRow title="Editor's Picks" emoji="🏆" playlists={sections.editors_picks ?? []} />
                                <SectionRow title="Because You Liked" emoji="💜" playlists={sections.because_you_liked?.playlists ?? []} />
                                <SectionRow title="New & Rising" emoji="🌱" playlists={sections.new_and_rising ?? []} />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* ─── Tab Heading ─────────────────────────────── */}
                    {activeTab !== 'for-you' && (
                        <p className="text-gray-400 text-sm mb-6">
                            {activeTab === 'following'
                                ? 'Latest playlists from people you follow, newest first.'
                                : 'Hottest playlists in the last 24 hours, ranked by likes & saves.'}
                        </p>
                    )}

                    {/* ─── Main Grid ───────────────────────────────── */}
                    {activeTab === 'for-you' && (
                        <div className="mt-8 mb-6">
                            <h2 className="text-2xl font-bold bg-clip-text text-transparent" style={{ backgroundImage: 'linear-gradient(90deg, #818cf8, #a78bfa)' }}>
                                More For You
                            </h2>
                            <p className="text-gray-400 text-sm mt-1 mb-4">Personalized recommendations based on your activity</p>
                        </div>
                    )}

                    {activeQuery.isLoading ? (
                        <SkeletonGrid />
                    ) : playlists.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                            className="text-center py-20 rounded-xl border border-dashed"
                            style={{ background: 'rgba(30,35,54,0.5)', borderColor: '#2a3050' }}
                        >
                            <motion.div
                                animate={{ y: [0, -8, 0] }}
                                transition={{ repeat: Infinity, duration: 2.4, ease: 'easeInOut' }}
                                className="text-5xl mb-4"
                            >
                                {activeTab === 'following' ? '👥' : activeTab === 'trending' ? '🔥' : '✨'}
                            </motion.div>
                            <h3 className="text-xl font-medium text-gray-300 mb-2">No playlists found</h3>
                            <p className="text-gray-500 max-w-sm mx-auto">
                                {activeTab === 'following'
                                    ? "You're not following anyone yet, or they haven't created any playlists. Go follow some creators!"
                                    : 'Try adjusting your filters or check back later!'}
                            </p>
                        </motion.div>
                    ) : (
                        <>
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={`${activeTab}-${selectedCategory}-${selectedDuration}-${page}`}
                                    variants={gridVariants}
                                    initial="hidden"
                                    animate="show"
                                    className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8"
                                >
                                    {playlists.map((playlist) => (
                                        <motion.div key={playlist.id} variants={cardVariants} transition={{ duration: 0.5, ease: 'easeOut' }}>
                                            <PlaylistCard playlist={playlist} />
                                        </motion.div>
                                    ))}
                                </motion.div>
                            </AnimatePresence>

                            {/* Pagination */}
                            <div className="flex justify-center items-center gap-4 mt-4">
                                <motion.button
                                    whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                                    onClick={() => setPage(p => Math.max(p - 1, 1))}
                                    disabled={page === 1}
                                    className="px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
                                    style={{ background: '#1e2336' }}
                                >
                                    Previous
                                </motion.button>
                                <span className="text-sm text-gray-400">Page {page} of {totalPages || 1}</span>
                                <motion.button
                                    whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                                    onClick={() => { if (hasNext) setPage(p => p + 1); }}
                                    disabled={!hasNext}
                                    className="px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
                                    style={{ background: '#1e2336' }}
                                >
                                    Next
                                </motion.button>
                            </div>
                        </>
                    )}
                </main>
            </div>
        </ProtectedRoute>
    );
}
