"use client";

import { useQuery } from "@tanstack/react-query";
import { UsersService } from "@/lib/api";
import { motion } from "framer-motion";
import { X, User, Loader2 } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

interface FollowListModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: "followers" | "following";
    userId: number;
}

export default function FollowListModal({ isOpen, onClose, type, userId }: FollowListModalProps) {
    const { data: users, isLoading } = useQuery({
        queryKey: [type, userId],
        queryFn: () =>
            type === "followers"
                ? UsersService.getUserFollowersApiUsersUserIdFollowersGet(userId)
                : UsersService.getUserFollowingApiUsersUserIdFollowingGet(userId),
        enabled: isOpen,
    });

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-[#121212] border border-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl h-[500px] flex flex-col"
            >
                <div className="flex items-center justify-between p-4 border-b border-white/10 shrink-0">
                    <h2 className="text-xl font-bold text-white capitalize">{type}</h2>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                <div className="overflow-y-auto flex-1 p-2">
                    {isLoading ? (
                        <div className="flex justify-center items-center h-full text-gray-500 gap-2">
                            <Loader2 className="animate-spin" /> Loading...
                        </div>
                    ) : users && users.length > 0 ? (
                        <div className="space-y-2">
                            {users.map((u) => (
                                <Link
                                    key={u.id}
                                    href={`/user/${u.username}`}
                                    onClick={onClose}
                                    className="flex items-center gap-4 p-3 hover:bg-white/5 rounded-xl transition-colors group"
                                >
                                    <div className="relative w-10 h-10 rounded-full overflow-hidden bg-zinc-800 shrink-0 border border-white/10">
                                        {u.profile_image ? (
                                            <Image src={u.profile_image} alt={u.username} fill className="object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-500">
                                                <User size={16} />
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-white font-medium truncate group-hover:text-purple-400 transition-colors">
                                            {u.full_name || u.username}
                                        </h3>
                                        <p className="text-gray-500 text-sm truncate">@{u.username}</p>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-2">
                            <User size={48} className="opacity-20" />
                            <p>No {type} yet.</p>
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
}
