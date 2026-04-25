'use client';

import { PlaylistResponse } from "@/lib/api/models/PlaylistResponse";
import NextLink from "next/link";
import { Play, Lock, Globe, Gamepad2, Film, Hash, Heart } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { CATEGORY_GAMING } from "@/lib/constants";
import { useState } from "react";

interface PlaylistCardProps {
    playlist: PlaylistResponse;
}

export function PlaylistCard({ playlist }: PlaylistCardProps) {
    const isGaming = playlist.category === CATEGORY_GAMING;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{
                y: -6,
                boxShadow: "0 20px 40px rgba(0,0,0,0.35)",
                transition: { duration: 0.2 },
            }}
            className="group h-full"
        >
            <NextLink href={`/playlists/${playlist.id}`} className="block h-full">
                <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-500/50 transition-colors shadow-lg h-full flex flex-col">
                    {/* Thumbnail */}
                    <div className="aspect-video bg-gray-700 relative overflow-hidden">
                        {playlist.thumbnail ? (
                            /* eslint-disable-next-line @next/next/no-img-element */
                            <img
                                src={playlist.thumbnail}
                                alt={playlist.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-900 to-zinc-900 relative overflow-hidden group-hover:scale-105 transition-transform duration-500">
                                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white to-transparent"></div>
                                <Play className="text-white/40 drop-shadow-lg z-10" size={56} />
                            </div>
                        )}

                        {/* Hover overlay */}
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div className="bg-blue-600 rounded-full p-3 transform scale-75 group-hover:scale-100 transition-transform duration-300">
                                <Play className="text-white fill-white ml-1" size={24} />
                            </div>
                        </div>

                        {/* Video count */}
                        <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded font-medium">
                            {playlist.video_count} videos
                        </div>

                        {/* Privacy */}
                        <div className="absolute top-2 left-2 bg-black/60 p-1.5 rounded-full backdrop-blur-sm">
                            {playlist.is_public ? <Globe size={14} className="text-gray-300" /> : <Lock size={14} className="text-gray-300" />}
                        </div>

                        {/* Category */}
                        {playlist.category && (
                            <div className="absolute top-2 right-2 bg-black/60 p-1.5 rounded-full backdrop-blur-sm flex items-center gap-1 px-2">
                                {isGaming ? <Gamepad2 size={12} className="text-purple-400" /> : <Film size={12} className="text-pink-400" />}
                                <span className="text-[10px] font-bold tracking-wide uppercase text-white">
                                    {playlist.category}
                                </span>
                            </div>
                        )}
                    </div>

                    <div className="p-4 flex-1 flex flex-col">
                        <h3 className="text-lg font-semibold text-white mb-1 line-clamp-1 group-hover:text-blue-400 transition-colors">
                            {playlist.title}
                        </h3>

                        {playlist.hook_description ? (
                            <p className="text-blue-200 text-sm italic mb-3 line-clamp-2 flex-1">
                                &quot;{playlist.hook_description}&quot;
                            </p>
                        ) : playlist.description && (
                            <p className="text-gray-400 text-sm line-clamp-2 mb-3 flex-1">
                                {playlist.description}
                            </p>
                        )}

                        {(playlist.scenario || (playlist.vibes && playlist.vibes.length > 0)) && (
                            <div className="flex flex-wrap gap-1.5 mt-auto mb-3">
                                {playlist.scenario && (
                                    <span className="text-[10px] px-1.5 py-0.5 bg-gray-700 text-gray-300 rounded border border-gray-600">
                                        {playlist.scenario}
                                    </span>
                                )}
                                {playlist.vibes?.slice(0, 2).map(vibe => (
                                    <span key={vibe} className="text-[10px] px-1.5 py-0.5 bg-gray-700 text-gray-300 rounded border border-gray-600 flex items-center gap-1">
                                        <Hash size={8} />
                                        {vibe}
                                    </span>
                                ))}
                            </div>
                        )}

                        <div className="flex justify-between items-center pt-2 border-t border-gray-700 mt-auto">
                            <div className="flex items-center gap-2">
                                {playlist.owner_username && (
                                    <span className="text-xs text-gray-400">
                                        by <span className="text-gray-300">@{playlist.owner_username}</span>
                                    </span>
                                )}
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                                {playlist.likes_count !== undefined && (
                                    <div className="flex items-center gap-1">
                                        {/* Pop animation on heart */}
                                        <motion.div
                                            animate={playlist.is_liked_by_me ? { scale: [1, 1.45, 1] } : {}}
                                            transition={{ duration: 0.35 }}
                                        >
                                            <Heart
                                                size={14}
                                                fill={playlist.is_liked_by_me ? "#ef4444" : "none"}
                                                stroke={playlist.is_liked_by_me ? "#ef4444" : "currentColor"}
                                                strokeWidth={2}
                                            />
                                        </motion.div>
                                        {/* Count ticker — animates when value changes */}
                                        <AnimatePresence mode="popLayout">
                                            <motion.span
                                                key={playlist.likes_count}
                                                initial={{ y: -8, opacity: 0 }}
                                                animate={{ y: 0, opacity: 1 }}
                                                exit={{ y: 8, opacity: 0 }}
                                                transition={{ duration: 0.2 }}
                                            >
                                                {playlist.likes_count}
                                            </motion.span>
                                        </AnimatePresence>
                                    </div>
                                )}
                                <span>{new Date(playlist.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </NextLink>
        </motion.div>
    );
}
