'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2 } from 'lucide-react';
import { useCreatePlaylist } from '@/lib/hooks/usePlaylists';
import { PlaylistCreate } from '@/lib/api/models/PlaylistCreate';
import {
    VALID_CATEGORIES,
    getValidScenarios,
    getValidVibes
} from '@/lib/constants';

interface PlaylistCreateModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function PlaylistCreateModal({ isOpen, onClose }: PlaylistCreateModalProps) {
    const createPlaylistMutation = useCreatePlaylist();

    // Form State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [isPublic, setIsPublic] = useState(true);
    const [category, setCategory] = useState<string>('');
    const [scenario, setScenario] = useState<string>('');
    const [vibes, setVibes] = useState<string[]>([]);
    const [hookDescription, setHookDescription] = useState('');

    const resetForm = () => {
        setTitle('');
        setDescription('');
        setIsPublic(true);
        setCategory('');
        setScenario('');
        setVibes([]);
        setHookDescription('');
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    // Handle Category Change (Reset dependent fields)
    const handleCategoryChange = (newCategory: string) => {
        setCategory(newCategory);
        setScenario('');
        setVibes([]);
    };

    const handleVibeToggle = (vibe: string) => {
        if (vibes.includes(vibe)) {
            setVibes(vibes.filter(v => v !== vibe));
        } else {
            if (vibes.length < 2) {
                setVibes([...vibes, vibe]);
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;

        const createData: PlaylistCreate = {
            title,
            description: description || null,
            is_public: isPublic,
            category: category || null,
            scenario: scenario || null,
            vibes: vibes.length > 0 ? vibes : null,
            hook_description: hookDescription || null,
        };

        createPlaylistMutation.mutate(createData, {
            onSuccess: () => {
                handleClose();
            }
        });
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                        onClick={handleClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ duration: 0.2 }}
                        className="bg-gray-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto border border-gray-700 relative z-10"
                    >
                        <div className="flex justify-between items-center p-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-20">
                            <h3 className="text-lg font-semibold text-white">Create New Playlist</h3>
                            <button
                                onClick={handleClose}
                                className="text-gray-400 hover:text-white transition"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-4 space-y-4">
                            {/* Title */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Title <span className="text-red-400">*</span>
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="My Awesome Playlist"
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            {/* Description */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="What's this collection about?"
                                    rows={3}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                />
                            </div>

                            {/* Category */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Category
                                </label>
                                <select
                                    value={category}
                                    onChange={(e) => handleCategoryChange(e.target.value)}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Select a category...</option>
                                    {VALID_CATEGORIES.map(cat => (
                                        <option key={cat} value={cat}>{cat}</option>
                                    ))}
                                </select>
                            </div>

                            {category && (
                                <>
                                    {/* Scenario */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-1">
                                            Scenario
                                        </label>
                                        <select
                                            value={scenario}
                                            onChange={(e) => setScenario(e.target.value)}
                                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="">Select a scenario...</option>
                                            {getValidScenarios(category).map(scen => (
                                                <option key={scen} value={scen}>{scen}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Vibes */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Vibes (Max 2)
                                        </label>
                                        <div className="flex flex-wrap gap-2">
                                            {getValidVibes(category).map(vibe => (
                                                <button
                                                    key={vibe}
                                                    type="button"
                                                    onClick={() => handleVibeToggle(vibe)}
                                                    className={`px-3 py-1 text-xs rounded-full border transition-colors ${vibes.includes(vibe)
                                                        ? 'bg-blue-600 border-blue-600 text-white'
                                                        : 'bg-transparent border-gray-600 text-gray-400 hover:border-gray-500'
                                                        } ${!vibes.includes(vibe) && vibes.length >= 2 ? 'opacity-50 cursor-not-allowed' : ''
                                                        }`}
                                                    disabled={!vibes.includes(vibe) && vibes.length >= 2}
                                                >
                                                    {vibe}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Hook Description */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-1">
                                            The Hook <span className="text-xs text-gray-500">(Max 140 chars)</span>
                                        </label>
                                        <input
                                            type="text"
                                            maxLength={140}
                                            value={hookDescription}
                                            onChange={(e) => setHookDescription(e.target.value)}
                                            placeholder="Catchy one-liner..."
                                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                        <div className="text-xs text-right text-gray-500 mt-1">
                                            {hookDescription.length}/140
                                        </div>
                                    </div>
                                </>
                            )}

                            {/* Visibility Toggle */}
                            <div className="flex items-center gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setIsPublic(!isPublic)}
                                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${isPublic ? 'bg-blue-600' : 'bg-gray-600'
                                        }`}
                                >
                                    <span
                                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isPublic ? 'translate-x-6' : 'translate-x-1'
                                            }`}
                                    />
                                </button>
                                <span className="text-sm font-medium text-gray-300">
                                    {isPublic ? 'Public' : 'Private'}
                                </span>
                            </div>

                            {/* Actions */}
                            <div className="pt-4 flex justify-end gap-3 border-t border-gray-700">
                                <button
                                    type="button"
                                    onClick={handleClose}
                                    className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={createPlaylistMutation.isPending}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 disabled:opacity-50"
                                >
                                    {createPlaylistMutation.isPending && <Loader2 className="animate-spin" size={16} />}
                                    {createPlaylistMutation.isPending ? 'Creating...' : 'Create Playlist'}
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
