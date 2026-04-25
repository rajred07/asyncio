"use client";

import { useState } from "react";
import { UserResponse, UserPublicProfile } from "@/lib/api";
import { UsersService } from "@/lib/api";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { User, Calendar, Edit2 } from "lucide-react";
import Image from "next/image";
import { format } from "date-fns";
import EditProfileModal from "@/components/EditProfileModal";
import FollowListModal from "@/components/FollowListModal";
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { useEffect } from "react";

interface ProfileHeaderProps {
    user: UserResponse | UserPublicProfile;
    isPrivate: boolean;
    onEdit?: () => void;
    currentUser?: UserResponse;
}

const ProfileHeader = ({ user, isPrivate }: ProfileHeaderProps) => {
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [activeFollowList, setActiveFollowList] = useState<"followers" | "following" | null>(null);

    // Parallax banner
    const { scrollY } = useScroll();
    const bannerY = useTransform(scrollY, [0, 300], [0, 75]);

    const queryClient = useQueryClient();

    // Determine if we are following this user (for public profiles)
    // Note: The API doesn't explicitly return "is_following", so we might need to check if the current user follows this user
    // For now, let's assume valid "Follow" button logic requires checking the relationship or handling optimistically
    // Since the API doesn't give us "is_following" directly in UserPublicProfile (based on schema), 
    // we might need to rely on error handling or a separate check. 
    // However, simpler approach: The backend should ideally tell us. 
    // If not, we will try to follow, and if 400/409, assume followed? 
    // Or maybe we can't fully know without that field. 
    // Let's implement the basic structure first.

    // Actually, wait, usually the backend returns `is_following` boolean. 
    // Checking the schema: UserPublicProfile doesn't seem to have `is_following`.
    // This is a common pattern issue. I'll implement the UI assuming we might need to just show "Follow" 
    // and handle the state locally or refetch. 
    // Or, maybe I can fetch "my following" list and check if this user is in it? That's expensive.
    // For this MVF (Minimum Viable Feature), I'll just show Follow/Unfollow based on a local state initialized by... nothing?
    // Okay, checking `UserPublicProfile` might be useful.
    // Let's check `UserResponse` again.
    // It has `followers_count` and `following_count`.

    // Let's use a optimistic approach or just a simple toggle that might error if state is wrong.
    // BUT, for a good UX, we need to know.
    // I will add a check: I'll optimistically assume "Follow" is available if not me.

    const { user: authUser } = useAuth();

    // Fetch whom the current user follows to see if this profile is in the list
    const { data: myFollowing } = useQuery({
        queryKey: ["following", authUser?.id],
        queryFn: () => UsersService.getUserFollowingApiUsersUserIdFollowingGet(authUser!.id),
        enabled: !!authUser && !isPrivate,
    });

    const [isFollowing, setIsFollowing] = useState(false);

    useEffect(() => {
        if (myFollowing) {
            setIsFollowing(myFollowing.some((u: UserPublicProfile) => u.id === user.id));
        }
    }, [myFollowing, user.id]);

    const followMutation = useMutation({
        mutationFn: (userId: number) => UsersService.followUserApiUsersUserIdFollowPost(userId),
        onSuccess: () => {
            setIsFollowing(true);
            toast.success(`Followed ${user.username}`);
            // Optimistically update count
            if ('followers_count' in user && user.followers_count != null) user.followers_count += 1;
            queryClient.invalidateQueries({ queryKey: ["user", user.username] });
            queryClient.invalidateQueries({ queryKey: ["following", authUser?.id] });
        },
        onError: (error) => {
            console.error(error);
            toast.error("Failed to follow user");
        },
    });

    const unfollowMutation = useMutation({
        mutationFn: (userId: number) => UsersService.unfollowUserApiUsersUserIdFollowDelete(userId),
        onSuccess: () => {
            setIsFollowing(false);
            toast.success(`Unfollowed ${user.username}`);
            if ('followers_count' in user && user.followers_count != null) user.followers_count = Math.max(0, user.followers_count - 1);
            queryClient.invalidateQueries({ queryKey: ["user", user.username] });
            queryClient.invalidateQueries({ queryKey: ["following", authUser?.id] });
        },
        onError: (error) => {
            console.error(error);
            toast.error("Failed to unfollow user");
        },
    });

    const handleFollowToggle = () => {
        if (isFollowing) {
            unfollowMutation.mutate(user.id);
        } else {
            followMutation.mutate(user.id);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto p-6">
            {/* Parallax Banner */}
            <div className="h-44 w-full rounded-t-3xl relative overflow-hidden">
                <motion.div
                    style={{
                        y: bannerY,
                        background: 'linear-gradient(135deg, #6C63FF 0%, #8b5cf6 100%)',
                        position: 'absolute',
                        inset: 0,
                    }}
                />
                {/* Shine highlight */}
                <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at 25% 40%, rgba(255,255,255,0.12) 0%, transparent 55%)' }} />
                {/* Bottom fade into card */}
                <div className="absolute bottom-0 left-0 right-0 h-24" style={{ background: 'linear-gradient(to bottom, transparent, rgba(15,17,26,0.75))' }} />
            </div>

            <div
                className="backdrop-blur-md rounded-b-3xl p-6 -mt-16 relative z-10 shadow-xl border-x border-b"
                style={{
                    background: 'linear-gradient(180deg, rgba(108,99,255,0.07) 0%, rgba(14,16,26,0.97) 30%)',
                    borderColor: '#1e2336',
                }}
            >
                <div className="flex flex-col md:flex-row items-end md:items-center justify-between gap-6">
                    <div className="flex items-end gap-6">
                        <div className="relative">
                            <div className="w-32 h-32 rounded-full border-4 overflow-hidden"
                                style={{ borderColor: '#0f111a', background: '#1e2336' }}>
                                {user.profile_image ? (
                                    <Image
                                        src={user.profile_image}
                                        alt={user.username}
                                        fill
                                        className="object-cover"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-4xl text-gray-500">
                                        <User />
                                    </div>
                                )}
                            </div>
                            {isPrivate && (
                                <button
                                    onClick={() => setIsEditModalOpen(true)}
                                    className="absolute bottom-0 right-0 p-2 rounded-full transition-colors border-4"
                                    style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderColor: '#0f111a' }}
                                >
                                    <Edit2 size={16} className="text-white" />
                                </button>
                            )}
                        </div>

                        <div className="mb-2">
                            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                                {user.full_name || user.username}
                                {!isPrivate && isFollowing && (
                                    <span className="text-xs px-2 py-1 rounded-full" style={{ background: '#1e2336', color: '#818cf8', border: '1px solid rgba(99,102,241,0.3)' }}>Following</span>
                                )}
                            </h1>
                            <p className="text-gray-400">@{user.username}</p>
                        </div>
                    </div>

                    <div className="flex gap-4 mb-2">
                        {!isPrivate && (
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleFollowToggle}
                                className={`px-6 py-2 rounded-full font-semibold transition-all ${isFollowing
                                    ? 'text-gray-300 border'
                                    : 'text-white'
                                    }`}
                                style={isFollowing
                                    ? { background: '#1e2336', borderColor: '#2a3050' }
                                    : { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }
                                }
                            >
                                {isFollowing ? "Unfollow" : "Follow"}
                            </motion.button>
                        )}

                        {isPrivate && (
                            <div className="flex gap-2">
                                {/* Placeholder for settings or direct edit */}
                            </div>
                        )}
                    </div>
                </div>

                {/* Bio & Details */}
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="md:col-span-2 space-y-4">
                        {user.bio ? (
                            <p className="text-gray-300 leading-relaxed text-lg">{user.bio}</p>
                        ) : (
                            <p className="text-gray-500 italic">No bio yet.</p>
                        )}

                        <div className="flex flex-wrap gap-4 text-sm text-gray-400 mt-4">
                            <div className="flex items-center gap-1">
                                <Calendar size={14} />
                                Joined {format(new Date(user.created_at), 'MMMM yyyy')}
                            </div>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="flex justify-around md:justify-end gap-8 p-4 rounded-2xl border" style={{ background: 'rgba(30,35,54,0.6)', borderColor: '#1e2336' }}>
                        <button
                            onClick={() => setActiveFollowList("followers")}
                            className="text-center hover:opacity-80 transition-opacity"
                        >
                            <div className="text-2xl font-bold text-white">{user.followers_count}</div>
                            <div className="text-xs text-gray-400 uppercase tracking-wider">Followers</div>
                        </button>
                        <div className="w-px bg-white/10"></div>
                        <button
                            onClick={() => setActiveFollowList("following")}
                            className="text-center hover:opacity-80 transition-opacity"
                        >
                            <div className="text-2xl font-bold text-white">{user.following_count}</div>
                            <div className="text-xs text-gray-400 uppercase tracking-wider">Following</div>
                        </button>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {isEditModalOpen && isPrivate && (
                    <EditProfileModal
                        isOpen={isEditModalOpen}
                        onClose={() => setIsEditModalOpen(false)}
                        user={user as UserResponse}
                    />
                )}

                {activeFollowList && (
                    <FollowListModal
                        isOpen={!!activeFollowList}
                        onClose={() => setActiveFollowList(null)}
                        type={activeFollowList}
                        userId={user.id}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

export default ProfileHeader;
