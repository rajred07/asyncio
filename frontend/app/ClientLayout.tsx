'use client';

import { usePathname } from 'next/navigation';
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "react-hot-toast";
import QueryProvider from "@/components/QueryProvider";
import { FloatingIslandNav } from "@/components/FloatingIslandNav";
import { GlobalFAB } from "@/components/GlobalFAB";

export default function ClientLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const isAuthPage = pathname === '/login' || pathname === '/signup';

    return (
        <AuthProvider>
            <QueryProvider>
                <Toaster position="bottom-right" />
                {children}
                {!isAuthPage && <GlobalFAB />}
                {!isAuthPage && <FloatingIslandNav />}
            </QueryProvider>
        </AuthProvider>
    );
}
