"use client";

import { useQuery } from "@tanstack/react-query";
import { UsersService } from "@/lib/api";
import ProfileHeader from "@/components/ProfileHeader";
import { Loader2, Trash2, AlertTriangle, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ProfilePage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

    const { data: user, isLoading, error } = useQuery({
        queryKey: ["currentUser"],
        queryFn: UsersService.getCurrentUserProfileApiUsersMeGet,
        retry: false, // Don't retry if 401, just redirect or show error
    });

    const deleteAccountMutation = useMutation({
        mutationFn: UsersService.deleteCurrentUserApiUsersMeDelete,
        onSuccess: () => {
            toast.success("Account deleted successfully.");
            // Clear token and redirect
            localStorage.removeItem("token");
            queryClient.clear();
            router.push("/login");
        },
        onError: (err) => {
            console.error(err);
            toast.error("Failed to delete account.");
        },
    });

    const handleLogout = () => {
        localStorage.removeItem("token");
        queryClient.clear();
        toast.success("Logged out successfully");
        router.push("/login");
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20">
                <Loader2 className="animate-spin text-purple-500" size={48} />
            </div>
        );
    }

    if (error || !user) {
        // Ideally redirect to login or show error
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center">
                <h2 className="text-2xl font-bold text-white mb-4">Please Log In</h2>
                <p className="text-gray-400 mb-6">You need to be logged in to view your profile.</p>
                <button
                    onClick={() => router.push("/login")}
                    className="px-6 py-2 rounded-full text-white font-semibold transition-colors"
                    style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                >
                    Go to Login
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen pb-20" style={{ background: '#0f111a' }}>
            <div className="container mx-auto px-4 pt-4">
                <ProfileHeader user={user} isPrivate={true} />

                <div className="max-w-4xl mx-auto px-6 mt-12 space-y-12">
                    {/* Account Settings / Actions */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="rounded-2xl p-6 border" style={{ background: '#13162a', borderColor: '#1e2336' }}>
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <LogOut size={20} style={{ color: '#818cf8' }} />
                                Account Actions
                            </h3>
                            <p className="text-gray-500 mb-6 text-sm">
                                Manage your session.
                            </p>
                            <button
                                onClick={handleLogout}
                                className="w-full py-3 rounded-xl text-white transition-colors flex items-center justify-center gap-2 border"
                                style={{ borderColor: '#1e2336', background: 'rgba(30,35,54,0.5)' }}
                                onMouseEnter={e => (e.currentTarget.style.background = '#1e2336')}
                                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(30,35,54,0.5)')}
                            >
                                Sign Out
                            </button>
                        </div>

                        <div className="rounded-2xl p-6 relative overflow-hidden border" style={{ background: '#13162a', borderColor: 'rgba(239,68,68,0.2)' }}>
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <AlertTriangle size={64} className="text-red-500" />
                            </div>
                            <h3 className="text-xl font-bold text-red-500 mb-4 flex items-center gap-2">
                                <Trash2 size={20} />
                                Danger Zone
                            </h3>
                            <p className="text-gray-400 mb-6 text-sm">
                                Permanently delete your account and all data. This action cannot be undone.
                            </p>
                            <button
                                onClick={() => setIsDeleteModalOpen(true)}
                                className="w-full py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl text-red-400 transition-colors flex items-center justify-center gap-2"
                            >
                                Delete Account
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {isDeleteModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-[#13162a] border border-[#1e2336] rounded-2xl w-full max-w-md p-6 shadow-2xl"
                        >
                            <h2 className="text-xl font-bold text-white mb-2">Delete Account?</h2>
                            <p className="text-gray-400 mb-6">
                                Are you sure you want to delete your account? This action is irreversible and will delete all your playlists and data.
                            </p>
                            <div className="flex justify-end gap-3">
                                <button
                                    onClick={() => setIsDeleteModalOpen(false)}
                                    className="px-4 py-2 rounded-lg hover:bg-white/5 text-gray-300 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => deleteAccountMutation.mutate()}
                                    disabled={deleteAccountMutation.isPending}
                                    className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                                >
                                    {deleteAccountMutation.isPending && <Loader2 className="animate-spin" size={16} />}
                                    Confirm Delete
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
