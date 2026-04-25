"use client";

import { useQuery } from "@tanstack/react-query";
import { UsersService } from "@/lib/api";
import ProfileHeader from "@/components/ProfileHeader";
import { Loader2, ArrowLeft } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function PublicProfilePage() {
    const params = useParams();
    const username = params.username as string;
    const router = useRouter();

    const { data: user, isLoading, error } = useQuery({
        queryKey: ["user", username],
        queryFn: () => UsersService.getUserByUsernameApiUsersUsernameGet(username),
        retry: 1,
    });

    // Optional: fetch current user to pass to ProfileHeader if needed for "Is Me" check
    // But ProfileHeader can just check if user.id === currentUser.id if we passed currentUser
    // For now we assume "isPrivate={false}" means it's viewed as a public profile. 
    // If I view my OWN public profile link, it shows as public. That's fine.

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20">
                <Loader2 className="animate-spin text-purple-500" size={48} />
            </div>
        );
    }

    if (error || !user) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center px-4">
                <h2 className="text-3xl font-bold text-white mb-4">User Not Found</h2>
                <p className="text-gray-400 mb-8 max-w-md">The user "@{username}" could not be found. They may have changed their username or deleted their account.</p>
                <Link
                    href="/"
                    className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-colors text-white flex items-center gap-2"
                >
                    <ArrowLeft size={18} />
                    Back to Home
                </Link>
            </div>
        );
    }

    return (
        <div className="min-h-screen pb-20">
            <div className="container mx-auto px-4 pt-4">
                <div className="mb-4">
                    <button
                        onClick={() => router.back()}
                        className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors ml-4 md:ml-0"
                    >
                        <ArrowLeft size={18} />
                        Back
                    </button>
                </div>

                <ProfileHeader user={user} isPrivate={false} />

                {/* Placeholder for User's Public Playlists - Essential for "Profile" feel */}
                <div className="max-w-4xl mx-auto px-6 mt-12">
                    <h3 className="text-2xl font-bold text-white mb-6">Public Playlists</h3>
                    <div className="p-12 text-center border border-dashed border-white/10 rounded-3xl bg-white/5">
                        <p className="text-gray-500">Public playlists coming soon...</p>
                        {/* Future: Iterate over user's playlists here */}
                    </div>
                </div>
            </div>
        </div>
    );
}
