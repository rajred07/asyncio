'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService } from '@/lib/api';
import { Users, User, Mail, Plus, Music, Shield, Trophy, Check, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import { CreateGroupModal } from './CreateGroupModal';

interface Props {
    selectedGroupId: number | null;
    onSelectGroup: (id: number) => void;
}

export function GroupListSidebar({ selectedGroupId, onSelectGroup }: Props) {
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const queryClient = useQueryClient();

    // Fetch groups and invites
    const { data: myGroups, isLoading } = useQuery({
        queryKey: ['my-group-playlists'],
        queryFn: () => GroupPlaylistsService.getMyGroupPlaylistsApiGroupPlaylistsGet(),
    });

    const { data: pendingInvites } = useQuery({
        queryKey: ['group-invites-pending'],
        queryFn: () => GroupPlaylistsService.getPendingInvitesApiGroupPlaylistsInvitesPendingGet(),
    });

    // Accept invite mutation
    const acceptInvite = useMutation({
        mutationFn: (inviteId: number) =>
            GroupPlaylistsService.acceptInviteApiGroupPlaylistsInvitesInviteIdAcceptPost(inviteId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-invites-pending'] });
            queryClient.invalidateQueries({ queryKey: ['my-group-playlists'] });
            toast.success('Joined group!');
        },
        onError: () => toast.error('Failed to accept invite')
    });

    // Reject invite mutation
    const rejectInvite = useMutation({
        mutationFn: (inviteId: number) =>
            GroupPlaylistsService.rejectInviteApiGroupPlaylistsInvitesInviteIdRejectPost(inviteId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['group-invites-pending'] });
            toast.success('Invite rejected');
        },
        onError: () => toast.error('Failed to reject invite')
    });

    return (
        <aside className="w-[350px] shrink-0 border-r border-[#1e2336] bg-[#0f111a] flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-[#1e2336] bg-[#0f111a]/40 flex items-center justify-between sticky top-0 z-10">
                <div className="flex items-center gap-2">
                    <Users className="text-purple-400" size={24} />
                    <h2 className="text-xl font-bold text-white tracking-tight">Groups</h2>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="p-2 bg-[#1e2336] hover:bg-gray-700 rounded-full text-gray-300 hover:text-white transition-colors"
                    title="New Group Playlist"
                >
                    <Plus size={20} />
                </button>
            </div>

            {/* Inbox Section (Visible only if pending invites exist) */}
            {pendingInvites && pendingInvites.length > 0 && (
                <div className="border-b border-gray-800 bg-gray-900/40 p-3">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center justify-between">
                        Inbox
                        <span className="bg-purple-600 text-white text-[10px] px-1.5 py-0.5 rounded-full">{pendingInvites.length}</span>
                    </h3>
                    <div className="space-y-2">
                        {pendingInvites.map((invite: any) => (
                            <div key={invite.id} className="bg-gray-800/80 rounded-lg p-3 text-sm border border-gray-700">
                                <p className="text-gray-300 font-medium mb-1 line-clamp-1">{invite.group_playlist_title}</p>
                                <p className="text-gray-500 text-xs mb-3">Invited by @{invite.inviter_username}</p>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => acceptInvite.mutate(invite.id)}
                                        className="flex-1 bg-purple-600 hover:bg-purple-700 text-white rounded py-1.5 text-xs font-medium transition flex justify-center items-center gap-1"
                                    >
                                        <Check size={14} /> Join
                                    </button>
                                    <button
                                        onClick={() => rejectInvite.mutate(invite.id)}
                                        className="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded py-1.5 text-xs font-medium transition flex justify-center items-center gap-1"
                                    >
                                        <X size={14} /> Decline
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* List */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent divide-y divide-[#1e2336]">
                {isLoading ? (
                    <div className="p-6 text-center text-sm text-gray-500">Loading your groups...</div>
                ) : myGroups?.length === 0 ? (
                    <div className="p-8 text-center flex flex-col items-center">
                        <Users size={32} className="text-gray-700 mb-3" />
                        <p className="text-sm text-gray-400 mb-4">You aren't in any groups yet.</p>
                        <button
                            onClick={() => setIsCreateModalOpen(true)}
                            className="bg-purple-600/20 text-purple-400 px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-600/30 transition-colors"
                        >
                            Create your first group
                        </button>
                    </div>
                ) : (
                    myGroups?.map((group: any) => {
                        const isSelected = selectedGroupId === group.id;
                        return (
                            <div
                                key={group.id}
                                onClick={() => onSelectGroup(group.id)}
                                className={`w-full text-left p-3 flex gap-3 items-center cursor-pointer transition-colors border-l-4 ${isSelected
                                    ? 'bg-[#1e2336]/80 border-purple-500'
                                    : 'hover:bg-[#1e2336]/40 border-transparent'
                                    }`}
                            >
                                {/* Thumbnail */}
                                <div className="w-14 h-14 rounded-full overflow-hidden bg-[#1e2336] shrink-0 relative flex items-center justify-center border border-[#1e2336]">
                                    {group.thumbnail ? (
                                        <img src={group.thumbnail} alt="" className="w-full h-full object-cover" />
                                    ) : (
                                        <Music size={24} className="text-gray-600" />
                                    )}
                                </div>

                                {/* Info */}
                                <div className="flex-1 min-w-0 flex flex-col justify-center">
                                    <h3 className={`font-semibold line-clamp-1 ${isSelected ? 'text-white' : 'text-gray-200'}`}>
                                        {group.title}
                                    </h3>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        {group.user_role === 'owner' ? (
                                            <Trophy size={12} className="text-yellow-500" />
                                        ) : group.user_role === 'admin' ? (
                                            <Shield size={12} className="text-gray-400" />
                                        ) : (
                                            <User size={12} className="text-gray-500" />
                                        )}
                                        <p className="text-xs text-gray-500 capitalize line-clamp-1">
                                            {group.user_role} • {group.is_public ? 'Public' : 'Private'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            <CreateGroupModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            />
        </aside>
    );
}
