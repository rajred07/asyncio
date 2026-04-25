"use client";

import { useState } from "react";
import { UserResponse, UsersService, UserUpdate } from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { X, Save, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

// If you don't have shadcn Dialog, we can build a custom one using motion
// I'll stick to a custom one based on recent patterns in this codebase if I don't see shadcn
// The previous files like PlaylistCreateModal use a custom implementation or headless UI? 
// Checking the file list, I see `PlaylistCreateModal.tsx`. 
// I'll use a similar pattern to `PlaylistCreateModal.tsx` for consistency.

interface EditProfileModalProps {
    isOpen: boolean;
    onClose: () => void;
    user: UserResponse;
}

export default function EditProfileModal({ isOpen, onClose, user }: EditProfileModalProps) {
    const [formData, setFormData] = useState<UserUpdate>({
        full_name: user.full_name || "",
        bio: user.bio || "",
        profile_image: user.profile_image || "",
        preferred_categories: (user as any).preferred_categories || [],
    });

    const CATEGORIES = ["Gaming", "Entertainment"];

    const toggleCategory = (cat: string) => {
        const current = formData.preferred_categories || [];
        const updated = current.includes(cat)
            ? current.filter((c) => c !== cat)
            : [...current, cat];
        setFormData({ ...formData, preferred_categories: updated });
    };

    const queryClient = useQueryClient();

    const mutation = useMutation({
        mutationFn: (data: UserUpdate) => UsersService.updateCurrentUserProfileApiUsersMePut(data),
        onSuccess: (updatedUser) => {
            toast.success("Profile updated successfully!");
            queryClient.setQueryData(["currentUser"], updatedUser);
            onClose();
        },
        onError: (error) => {
            console.error("Failed to update profile", error);
            toast.error("Failed to update profile.");
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(formData);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-[#121212] border border-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl"
            >
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <h2 className="text-xl font-bold text-white">Edit Profile</h2>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Full Name</label>
                        <input
                            type="text"
                            value={formData.full_name || ""}
                            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            placeholder="Your name"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Bio</label>
                        <textarea
                            value={formData.bio || ""}
                            onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all min-h-[100px] resize-none"
                            placeholder="Tell us about yourself..."
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Profile Image URL</label>
                        <input
                            type="url"
                            value={formData.profile_image || ""}
                            onChange={(e) => setFormData({ ...formData, profile_image: e.target.value })}
                            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            placeholder="https://example.com/avatar.jpg"
                        />
                        <p className="text-xs text-gray-500">Only direct image links supported for now.</p>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Content Preferences</label>
                        <p className="text-xs text-gray-500">Affects your personalised For You feed.</p>
                        <div className="flex gap-3 pt-1">
                            {CATEGORIES.map((cat) => {
                                const selected = (formData.preferred_categories || []).includes(cat);
                                return (
                                    <button
                                        key={cat}
                                        type="button"
                                        onClick={() => toggleCategory(cat)}
                                        className="px-5 py-2 rounded-full text-sm font-semibold border transition-all"
                                        style={selected
                                            ? { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderColor: 'transparent', color: '#fff' }
                                            : { background: '#1e2336', borderColor: '#2a3050', color: '#9ca3af' }
                                        }
                                    >
                                        {cat === "Gaming" ? "🎮 Gaming" : "🎬 Entertainment"}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div className="pt-4 flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg hover:bg-zinc-800 text-gray-300 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={mutation.isPending}
                            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {mutation.isPending ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                            Save Changes
                        </button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
