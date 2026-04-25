'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Lock, Globe, Loader2 } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService } from '@/lib/api';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

interface CreateGroupModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function CreateGroupModal({ isOpen, onClose }: CreateGroupModalProps) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [isPublic, setIsPublic] = useState(false);

    const queryClient = useQueryClient();
    const router = useRouter();

    const createMutation = useMutation({
        mutationFn: () => GroupPlaylistsService.createGroupPlaylistApiGroupPlaylistsPost({
            title,
            description: description || undefined
        }),
        onSuccess: (data) => {
            toast.success('Group playlist created!');
            queryClient.invalidateQueries({ queryKey: ['my-group-playlists'] });
            onClose();
            // Reset form
            setTitle('');
            setDescription('');
            setIsPublic(false);

            // Redirect to the new group
            router.push(`/group-playlists/${data.id}`);
        },
        onError: () => {
            toast.error('Failed to create group playlist');
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        createMutation.mutate();
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    className="relative w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl overflow-hidden"
                >
                    <div className="flex items-center justify-between p-6 border-b border-gray-800 bg-gray-900/50">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
                                <Users size={20} />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white">Create Group Playlist</h2>
                                <p className="text-xs text-gray-400">Start collaborating with friends</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-full transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="p-6 space-y-5">
                        <div className="space-y-2">
                            <label htmlFor="title" className="block text-sm font-medium text-gray-300">
                                Playlist Title *
                            </label>
                            <input
                                id="title"
                                type="text"
                                required
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full px-4 py-2.5 bg-gray-950 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow"
                                placeholder="e.g., Road Trip Bops"
                                autoFocus
                            />
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="description" className="block text-sm font-medium text-gray-300">
                                Description <span className="text-gray-500 font-normal">(optional)</span>
                            </label>
                            <textarea
                                id="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows={3}
                                className="w-full px-4 py-2.5 bg-gray-950 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow resize-none"
                                placeholder="What's this collection about?"
                            />
                        </div>

                        <div className="pt-4 flex gap-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={!title.trim() || createMutation.isPending}
                                className="flex-1 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                            >
                                {createMutation.isPending ? (
                                    <><Loader2 size={18} className="animate-spin" /> Creating...</>
                                ) : (
                                    'Create Space'
                                )}
                            </button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
