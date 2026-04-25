'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus } from 'lucide-react';
import { PlaylistCreateModal } from './PlaylistCreateModal';
import { usePathname } from 'next/navigation';

export function GlobalFAB() {
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const pathname = usePathname();

    // Hide FAB on distinct auth paths and Group Playlists (which has its own creation flow)
    if (pathname === '/login' || pathname === '/register' || pathname.startsWith('/group-playlists')) {
        return null;
    }

    return (
        <>
            <motion.button
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.95 }}
                transition={{
                    type: "spring",
                    stiffness: 400,
                    damping: 25,
                    rotate: { duration: 0.3 }
                }}
                onClick={() => setIsCreateModalOpen(true)}
                className="fixed bottom-24 right-6 sm:bottom-8 sm:right-8 z-50 bg-gradient-to-tr from-purple-600 to-blue-500 text-white p-4 rounded-full shadow-2xl hover:shadow-[0_0_20px_rgba(168,85,247,0.5)] flex items-center justify-center border border-white/20"
                title="Create New Playlist"
            >
                <Plus size={28} strokeWidth={2.5} />
            </motion.button>

            <PlaylistCreateModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            />
        </>
    );
}
