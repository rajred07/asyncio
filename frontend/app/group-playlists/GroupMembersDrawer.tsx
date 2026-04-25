import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GroupPlaylistsService, UsersService } from '@/lib/api';
import { Users, User, Shield, Trophy, UserPlus, X, Search, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
    playlistId: number;
    isOpen: boolean;
    onClose: () => void;
    playlistOwnerId: number;
    members: any[];
    currentUserRole: 'owner' | 'admin' | 'member';
    currentUserId?: number;
}

export function GroupMembersDrawer({ playlistId, isOpen, onClose, playlistOwnerId, members, currentUserRole, currentUserId }: Props) {
    const [inviteUsername, setInviteUsername] = useState('');
    const queryClient = useQueryClient();

    const inviteMutation = useMutation({
        mutationFn: async (username: string) => {
            try {
                const user = await UsersService.getUserByUsernameApiUsersUsernameGet(username);
                return await GroupPlaylistsService.inviteUserApiGroupPlaylistsPlaylistIdInvitePost(playlistId, { invitee_id: user.id });
            } catch (err: any) {
                if (err.status === 404) throw new Error("User not found");
                throw err;
            }
        },
        onSuccess: () => {
            toast.success(`Invite sent to ${inviteUsername}!`);
            setInviteUsername('');
        },
        onError: (err: any) => {
            toast.error(err.message || err.body?.detail || 'Failed to send invite');
        }
    });

    const handleInvite = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inviteUsername.trim()) return;
        inviteMutation.mutate(inviteUsername.trim());
    };

    const removeMutation = useMutation({
        mutationFn: (userId: number) => GroupPlaylistsService.removeMemberApiGroupPlaylistsPlaylistIdMembersUserIdDelete(playlistId, userId),
        onMutate: async (deletedUserId) => {
            await queryClient.cancelQueries({ queryKey: ['group-members', playlistId] });
            const previousMembers = queryClient.getQueryData(['group-members', playlistId]);
            queryClient.setQueryData(['group-members', playlistId], (old: any) =>
                old ? old.filter((m: any) => m.user_id !== deletedUserId) : []
            );
            return { previousMembers };
        },
        onError: (err, newTodo, context) => {
            queryClient.setQueryData(['group-members', playlistId], context?.previousMembers);
            toast.error('Failed to remove member');
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['group-members', playlistId] });
        }
    });

    const updateRoleMutation = useMutation({
        mutationFn: ({ userId, role }: { userId: number, role: 'admin' | 'member' }) =>
            GroupPlaylistsService.updateMemberRoleApiGroupPlaylistsPlaylistIdMembersUserIdRolePatch(playlistId, userId, { role: role as any }),
        onMutate: async ({ userId, role }) => {
            await queryClient.cancelQueries({ queryKey: ['group-members', playlistId] });
            const previousMembers = queryClient.getQueryData(['group-members', playlistId]);
            queryClient.setQueryData(['group-members', playlistId], (old: any) =>
                old ? old.map((m: any) => m.user_id === userId ? { ...m, role } : m) : []
            );
            return { previousMembers };
        },
        onError: (err, newTodo, context) => {
            queryClient.setQueryData(['group-members', playlistId], context?.previousMembers);
            toast.error('Failed to update role');
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['group-members', playlistId] });
        }
    });

    const handleRemove = (userId: number) => {
        removeMutation.mutate(userId);
        toast.success('Member removed');
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.aside
                    initial={{ x: 300, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 300, opacity: 0 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    className="w-[320px] shrink-0 border-l border-[#1e2336] bg-[#0f111a] flex flex-col h-full shadow-2xl z-30"
                >
                    {/* Header */}
                    <div className="h-16 px-4 border-b border-[#1e2336] flex items-center justify-between shrink-0 bg-[#0f111a]/80 backdrop-blur-sm">
                        <h2 className="font-semibold text-white flex items-center gap-2">
                            <Users size={18} className="text-purple-400" />
                            Group Members
                        </h2>
                        <button
                            onClick={onClose}
                            className="p-1.5 text-gray-400 hover:text-white hover:bg-[#1e2336] rounded-lg transition"
                        >
                            <X size={18} />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                        {/* Invite Section */}
                        {(currentUserRole === 'owner' || currentUserRole === 'admin') && (
                            <div className="space-y-3">
                                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Add Member</h3>
                                <form onSubmit={handleInvite} className="flex gap-2">
                                    <div className="relative flex-1">
                                        <input
                                            type="text"
                                            value={inviteUsername}
                                            onChange={(e) => setInviteUsername(e.target.value)}
                                            placeholder="Username..."
                                            className="w-full bg-[#1e2336]/60 border border-[#1e2336] rounded-lg py-2 px-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
                                            disabled={inviteMutation.isPending}
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={!inviteUsername.trim() || inviteMutation.isPending}
                                        className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded-lg flex items-center justify-center transition disabled:opacity-50"
                                    >
                                        {inviteMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />}
                                    </button>
                                </form>
                            </div>
                        )}

                        {/* Members List */}
                        <div className="space-y-3">
                            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Members ({members?.length || 0})</h3>
                            <div className="space-y-2">
                                {members?.map((member) => {
                                    const isSelf = member.user_id === currentUserId;
                                    const canRemove =
                                        !isSelf && (
                                            (currentUserRole === 'owner' && member.role !== 'owner') ||
                                            (currentUserRole === 'admin' && member.role === 'member')
                                        );

                                    return (
                                        <div key={member.id} className="flex items-center justify-between group p-2 rounded-xl hover:bg-[#1e2336]/40 border border-transparent hover:border-[#1e2336] transition">
                                            <div className="flex items-center gap-3 min-w-0">
                                                <div className="w-10 h-10 rounded-full bg-[#1e2336] border border-[#1e2336] flex items-center justify-center shrink-0 overflow-hidden">
                                                    {member.profile_image ? (
                                                        <img src={member.profile_image} alt="" className="w-full h-full object-cover" />
                                                    ) : (
                                                        <User size={16} className="text-gray-500" />
                                                    )}
                                                </div>
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-medium text-white truncate flex items-center gap-2">
                                                        {member.full_name || member.username}
                                                        {isSelf && <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded-sm uppercase tracking-widest font-bold">You</span>}
                                                    </p>
                                                    <div className="flex items-center gap-1.5 mt-0.5">
                                                        {member.role === 'owner' ? (
                                                            <Trophy size={10} className="text-yellow-500" />
                                                        ) : member.role === 'admin' ? (
                                                            <Shield size={10} className="text-purple-400" />
                                                        ) : null}
                                                        <p className="text-xs text-gray-500 capitalize">
                                                            {member.role}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Actions */}
                                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                {currentUserRole === 'owner' && member.role !== 'owner' && (
                                                    <select
                                                        value={member.role}
                                                        onChange={(e) => updateRoleMutation.mutate({ userId: member.user_id, role: e.target.value as 'admin' | 'member' })}
                                                        disabled={updateRoleMutation.isPending}
                                                        className="bg-[#1e2336] border border-[#2a2f45] text-xs text-gray-300 rounded shadow-sm focus:outline-none focus:ring-1 focus:ring-purple-500 px-1 py-1 disabled:opacity-50"
                                                    >
                                                        <option value="admin">Admin</option>
                                                        <option value="member">Member</option>
                                                    </select>
                                                )}

                                                {canRemove && (
                                                    <button
                                                        onClick={() => handleRemove(member.user_id)}
                                                        disabled={removeMutation.isPending}
                                                        className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition shrink-0 disabled:opacity-50 ml-1"
                                                        title="Remove Member"
                                                    >
                                                        <X size={14} />
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </motion.aside>
            )}
        </AnimatePresence>
    );
}
