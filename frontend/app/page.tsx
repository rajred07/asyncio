'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useMyPlaylists, useLikedPlaylists, useSavedPlaylists } from '@/lib/hooks/usePlaylists';
import { PlaylistCard } from '@/components/PlaylistCard';
import { Heart, Bookmark, ListMusic, Youtube } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { motion, AnimatePresence } from 'framer-motion';
import SyncInstructionsModal from '@/components/SyncInstructionsModal';

// Skeleton card for loading state
function SkeletonCard() {
  return (
    <div className="rounded-lg overflow-hidden border animate-pulse" style={{ background: '#1e2336', borderColor: '#2a3050' }}>
      <div className="aspect-video" style={{ background: '#252a42' }} />
      <div className="p-4 space-y-3">
        <div className="h-4 rounded w-3/4" style={{ background: '#252a42' }} />
        <div className="h-3 rounded w-1/2" style={{ background: '#252a42' }} />
        <div className="h-3 rounded w-1/3" style={{ background: '#252a42' }} />
      </div>
    </div>
  );
}

// Stagger container variants
const gridVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
} as const;
const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 },
} as const;

const TABS = [
  { id: 'my', label: 'My Playlists', icon: ListMusic },
  { id: 'liked', label: 'Liked', icon: Heart },
  { id: 'saved', label: 'Saved', icon: Bookmark },
] as const;

export default function Home() {
  const [activeTab, setActiveTab] = useState<'my' | 'liked' | 'saved'>('my');
  const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);

  const { data: myPlaylists = [], isLoading: isMyLoading } = useMyPlaylists();
  const { data: likedPlaylists = [], isLoading: isLikedLoading } = useLikedPlaylists();
  const { data: savedPlaylists = [], isLoading: isSavedLoading } = useSavedPlaylists();

  // Split watch later playlists out into their own section
  const watchlaterPlaylists = myPlaylists.filter((p: any) => p.scenario === 'watchlater');
  const regularPlaylists = myPlaylists.filter((p: any) => p.scenario !== 'watchlater');

  const getActiveData = () => {
    switch (activeTab) {
      case 'my': return { data: regularPlaylists, loading: isMyLoading, emptyText: "Create your first playlist to get started collecting videos.", emptyIcon: <ListMusic size={32} /> };
      case 'liked': return { data: likedPlaylists, loading: isLikedLoading, emptyText: "You haven't liked any playlists yet.", emptyIcon: <Heart size={32} /> };
      case 'saved': return { data: savedPlaylists, loading: isSavedLoading, emptyText: "You haven't saved any playlists to your library yet.", emptyIcon: <Bookmark size={32} /> };
    }
  };

  const { data: currentPlaylists, loading: isLoading, emptyText, emptyIcon } = getActiveData();

  return (
    <ProtectedRoute>
      <div className="min-h-screen text-white" style={{ background: '#0f111a' }}>
        <Navbar />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <motion.h1
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.35 }}
                className="text-3xl font-bold bg-clip-text text-transparent"
                style={{ backgroundImage: 'linear-gradient(90deg, #818cf8, #a78bfa)' }}
              >
                Dashboard
              </motion.h1>

              <motion.button
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.35, delay: 0.1 }}
                onClick={() => setIsSyncModalOpen(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 transition-all border border-indigo-500/30 hover:scale-105 active:scale-95"
                style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))' }}
              >
                <Youtube size={16} className="text-indigo-400" />
                How to Sync Watch Later
              </motion.button>
            </div>

            {/* Tabs with sliding pill */}
            <div className="flex p-1 rounded-lg self-start md:self-auto relative border" style={{ background: '#1e2336', borderColor: '#2a3050' }}>
              {TABS.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`relative flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors z-10 ${activeTab === id ? 'text-white' : 'text-gray-500 hover:text-gray-200'
                    }`}
                >
                  {activeTab === id && (
                    <motion.span
                      layoutId="dashboard-tab-pill"
                      className="absolute inset-0 rounded-md shadow"
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
          </div>

          {isLoading ? (
            // Skeleton shimmer grid
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {Array.from({ length: 10 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : currentPlaylists.length === 0 ? (
            // Animated empty state
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
                className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
                style={{ background: '#1e2336', color: '#818cf8' }}
              >
                {emptyIcon}
              </motion.div>
              <h3 className="text-xl font-medium text-gray-300 mb-2">No playlists found</h3>
              <p className="text-gray-500 max-w-sm mx-auto">{emptyText}</p>
            </motion.div>
          ) : (
            // Stagger grid
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                variants={gridVariants}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
              >
                {currentPlaylists.map((playlist) => (
                  <motion.div key={playlist.id} variants={cardVariants} transition={{ duration: 0.5, ease: "easeOut" }}>
                    <PlaylistCard playlist={playlist} />
                  </motion.div>
                ))}
              </motion.div>
            </AnimatePresence>
          )}
          {/* ═══════════════════════════════════════════════════
              WATCH LATER SORTED — only shown if user has imports
          ════════════════════════════════════════════════════ */}
          {watchlaterPlaylists.length > 0 && (
            <motion.section
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.15 }}
              className="mt-12"
            >
              {/* Section Header */}
              <div className="flex items-center gap-3 mb-5">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg" style={{ background: 'rgba(99,102,241,0.15)' }}>
                  <Youtube size={18} style={{ color: '#818cf8' }} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Watch Later Sorted</h2>
                  <p className="text-xs text-gray-500 mt-0.5">
                    AI-generated smart playlists from your YouTube Watch Later
                    &nbsp;·&nbsp; {watchlaterPlaylists.length} playlist{watchlaterPlaylists.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>

              {/* Horizontal scroll row */}
              <div className="flex gap-5 overflow-x-auto pb-3 -mx-1 px-1 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
                {watchlaterPlaylists.map((playlist: any, i: number) => (
                  <motion.div
                    key={playlist.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.35, delay: i * 0.07 }}
                    className="flex-shrink-0 w-56"
                  >
                    <PlaylistCard playlist={playlist} />
                  </motion.div>
                ))}
              </div>
            </motion.section>
          )}
        </main>

        {/* Sync Watch Later Instructions Modal */}
        <SyncInstructionsModal
          isOpen={isSyncModalOpen}
          onClose={() => setIsSyncModalOpen(false)}
        />
      </div>
    </ProtectedRoute>
  );
}
