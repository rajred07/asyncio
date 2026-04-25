'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { LayoutDashboard, PlaySquare, Users } from 'lucide-react';

const NAV_LINKS = [
    { href: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { href: '/feed', label: 'Feed', icon: <PlaySquare size={20} /> },
    { href: '/group-playlists', label: 'Groups', icon: <Users size={20} /> },
];

export function FloatingIslandNav() {
    const pathname = usePathname();
    const [isVisible, setIsVisible] = useState(true);
    const [lastScrollY, setLastScrollY] = useState(0);

    useEffect(() => {
        const handleScroll = () => {
            const currentScrollY = window.scrollY;

            // If scrolling DOWN, hide navbar. If scrolling UP, show it.
            // Also, always show it if we are very close to the top.
            if (currentScrollY > lastScrollY && currentScrollY > 50) {
                setIsVisible(false);
            } else if (currentScrollY < lastScrollY) {
                setIsVisible(true);
            }

            setLastScrollY(currentScrollY);
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, [lastScrollY]);

    // Don't render anything if we are on the login or register pages which have their own flow
    if (pathname === '/login' || pathname === '/register') {
        return null;
    }

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ y: 100, x: "-50%", opacity: 0 }}
                    animate={{ y: 0, x: "-50%", opacity: 1 }}
                    exit={{ y: 100, x: "-50%", opacity: 0 }}
                    transition={{
                        type: "spring",
                        stiffness: 400,
                        damping: 25,
                        mass: 0.8
                    }}
                    className="fixed bottom-6 left-1/2 z-[100]"
                >
                    <nav
                        className="flex items-center gap-1 p-1.5 rounded-full backdrop-blur-xl border shadow-2xl"
                        style={{
                            background: 'rgba(15,17,26,0.85)',
                            borderColor: '#1e2336',
                            boxShadow: '0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.08)',
                        }}
                    >
                        {NAV_LINKS.map(({ href, label, icon }) => {
                            const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));

                            return (
                                <Link
                                    key={href}
                                    href={href}
                                    className="relative px-5 py-2.5 rounded-full flex items-center gap-2 transition-colors whitespace-nowrap group"
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="floating-nav-bubble"
                                            className="absolute inset-0 rounded-full -z-10"
                                            style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                                            transition={{ type: "spring", stiffness: 300, damping: 24 }}
                                        />
                                    )}
                                    <div className={`flex items-center gap-2 transition-colors text-sm font-medium ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-200'}`}>
                                        {icon}
                                        <span className="hidden sm:block">{label}</span>
                                    </div>
                                </Link>
                            );
                        })}
                    </nav>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
