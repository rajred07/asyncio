'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { GroupListSidebar } from './GroupListSidebar';
import { GroupWorkspace } from './GroupWorkspace';
import { Navbar } from '@/components/Navbar';

export default function GroupPlaylistsPage() {
    const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null);

    return (
        <ProtectedRoute>
            <div className="flex flex-col min-h-screen bg-[#0f111a]">
                <Navbar />
                <div className="h-[calc(100vh-64px)] bg-[#0f111a] text-white flex overflow-hidden">
                    {/* LEFT PANE: Group List Sidebar (~350px wide) */}
                    <GroupListSidebar
                        selectedGroupId={selectedGroupId}
                        onSelectGroup={setSelectedGroupId}
                    />

                    {/* RIGHT PANE: Selected Group Workspace (Flex 1) */}
                    <GroupWorkspace
                        selectedGroupId={selectedGroupId}
                    />
                </div>
            </div>
        </ProtectedRoute>
    );
}
