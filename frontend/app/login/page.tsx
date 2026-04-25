'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { UsersService } from '@/lib/api/services/UsersService';
import { ApiError } from '@/lib/api/core/ApiError';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';

// --- Background Orbs matching app palette (#0f111a / blue-purple) ---
function FloatingOrbs() {
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            <motion.div
                className="absolute w-[600px] h-[600px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%)',
                    top: '-15%', right: '-5%',
                }}
                animate={{ scale: [1, 1.12, 1], x: [0, 25, 0], y: [0, -15, 0] }}
                transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
                className="absolute w-[500px] h-[500px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)',
                    bottom: '-10%', left: '-5%',
                }}
                animate={{ scale: [1, 1.18, 1], x: [0, -20, 0], y: [0, 25, 0] }}
                transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
            />
            <motion.div
                className="absolute w-[350px] h-[350px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%)',
                    top: '45%', left: '30%',
                }}
                animate={{ scale: [1, 1.25, 1] }}
                transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
            />
        </div>
    );
}

// --- Hero Card (left panel) ---
function HeroCard() {
    return (
        <motion.div
            className="relative"
            animate={{ rotateY: [0, 8, -8, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
            style={{ perspective: '1200px' }}
        >
            {/* Glow */}
            <motion.div
                className="absolute inset-0 rounded-2xl blur-2xl"
                style={{ background: 'rgba(99,102,241,0.4)', transform: 'scale(1.1)' }}
                animate={{ opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Card */}
            <div
                className="relative w-72 rounded-2xl p-5 flex flex-col gap-4"
                style={{
                    background: 'rgba(15,17,26,0.9)',
                    border: '1px solid rgba(99,102,241,0.4)',
                    backdropFilter: 'blur(24px)',
                }}
            >
                {/* Header row */}
                <div className="flex items-center gap-3">
                    <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                        style={{ background: 'rgba(99,102,241,0.25)', border: '1px solid rgba(99,102,241,0.4)' }}
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818cf8" strokeWidth="2.2">
                            <polygon points="5 3 19 12 5 21 5 3" />
                        </svg>
                    </div>
                    <div>
                        <p className="text-white font-semibold text-sm">Watch Later</p>
                        <p className="text-gray-500 text-xs">50 videos → 8 smart playlists</p>
                    </div>
                </div>

                {/* AI tag */}
                <div
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium"
                    style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)' }}
                >
                    <span>✨</span>
                    <span className="text-indigo-300">AI sorted instantly</span>
                </div>

                {/* Avatar row */}
                <div className="flex items-center gap-2">
                    {['🎬', '📽️', '🎥'].map((emoji, i) => (
                        <motion.div
                            key={i}
                            className="w-7 h-7 rounded-full text-xs flex items-center justify-center"
                            style={{ background: 'rgba(99,102,241,0.25)', border: '2px solid rgba(15,17,26,0.9)' }}
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ delay: 0.5 + i * 0.15 }}
                        >
                            {emoji}
                        </motion.div>
                    ))}
                    <span className="text-gray-500 text-xs ml-1">+87 more</span>
                </div>
            </div>
        </motion.div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-[#0f111a]" />}>
            <LoginPageInner />
        </Suspense>
    );
}

function LoginPageInner() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { login } = useAuth();
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [registeredMessage, setRegisteredMessage] = useState('');
    const [focusedField, setFocusedField] = useState<string | null>(null);

    useEffect(() => {
        if (searchParams.get('registered') === 'true') {
            setRegisteredMessage('Registration successful! Please login.');
        }
    }, [searchParams]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const response = await UsersService.loginApiUsersLoginPost({
                username: formData.username,
                password: formData.password,
            });
            await login(response.access_token);
            router.push('/');
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.body?.detail || 'Invalid credentials');
            } else {
                setError('An unexpected error occurred');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="min-h-screen flex items-center justify-center overflow-hidden relative"
            style={{ background: '#0f111a', fontFamily: "'Inter', sans-serif" }}
        >
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        .input-focused { box-shadow: 0 0 0 2px rgba(99,102,241,0.45), 0 0 20px rgba(99,102,241,0.12); }
        .btn-shine { position: relative; overflow: hidden; }
        .btn-shine::after { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent); transition: left 0.5s; }
        .btn-shine:hover::after { left: 100%; }
      `}</style>

            <FloatingOrbs />

            <div className="w-full max-w-5xl mx-auto px-6 flex items-center gap-20 relative z-10">

                {/* ──── LEFT PANEL ──── */}
                <motion.div
                    className="flex-1 hidden lg:flex flex-col gap-10"
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                >
                    {/* Logo */}
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="flex items-center gap-2"
                    >
                        <Sparkles size={24} className="text-indigo-400" />
                        <span
                            className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent"
                            style={{ backgroundImage: 'linear-gradient(135deg, #818cf8 0%, #c084fc 100%)' }}
                        >
                            Curate
                        </span>
                    </motion.div>

                    {/* Hero text */}
                    <div>
                        <motion.h1
                            className="text-5xl font-extrabold text-white leading-tight mb-4"
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2, duration: 0.7 }}
                        >
                            The social home for<br />
                            <span
                                className="bg-clip-text text-transparent"
                                style={{ backgroundImage: 'linear-gradient(90deg, #818cf8, #a78bfa)' }}
                            >
                                YouTube playlists.
                            </span>
                        </motion.h1>
                        <motion.p
                            className="text-gray-400 text-lg leading-relaxed"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.35, duration: 0.7 }}
                        >
                            Follow curators. Build together.<br />
                            <span className="text-gray-500">Let AI organize the rest.</span>
                        </motion.p>
                    </div>

                    {/* Animated card */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.55, duration: 0.8 }}
                        className="relative"
                    >
                        <HeroCard />
                        {/* Floating dots */}
                        {[...Array(5)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute w-1.5 h-1.5 rounded-full"
                                style={{
                                    background: i % 2 === 0 ? '#818cf8' : '#a78bfa',
                                    left: `${15 + i * 14}%`,
                                    top: `${20 + (i % 3) * 20}%`,
                                    opacity: 0.5,
                                }}
                                animate={{ y: [-6, 6, -6], opacity: [0.3, 0.8, 0.3] }}
                                transition={{ duration: 2 + i * 0.4, repeat: Infinity, delay: i * 0.25, ease: 'easeInOut' }}
                            />
                        ))}
                    </motion.div>
                </motion.div>

                {/* ──── RIGHT PANEL — Form Card ──── */}
                <motion.div
                    className="w-full max-w-md"
                    initial={{ opacity: 0, x: 50, scale: 0.97 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                >
                    <div
                        className="rounded-3xl p-8 relative"
                        style={{
                            background: 'rgba(14,16,26,0.85)',
                            border: '1px solid #1e2336',
                            backdropFilter: 'blur(32px)',
                            boxShadow: '0 0 80px rgba(99,102,241,0.08), 0 32px 64px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)',
                        }}
                    >
                        {/* Brand */}
                        <motion.div
                            className="text-center mb-7 flex items-center justify-center gap-2"
                            initial={{ opacity: 0, y: -15 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3, duration: 0.6 }}
                        >
                            <Sparkles size={28} className="text-indigo-400" />
                            <span
                                className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent"
                                style={{ backgroundImage: 'linear-gradient(135deg, #818cf8 0%, #c084fc 100%)' }}
                            >
                                Curate
                            </span>
                        </motion.div>

                        {/* Tab switcher */}
                        <motion.div
                            className="flex rounded-full p-1 mb-7 gap-1"
                            style={{ background: 'rgba(30,35,54,0.8)', border: '1px solid #1e2336' }}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.4 }}
                        >
                            <Link href="/signup" className="flex-1">
                                <div className="text-center py-2 rounded-full text-sm font-medium text-gray-500 hover:text-gray-300 transition-colors cursor-pointer">
                                    Sign Up
                                </div>
                            </Link>
                            <div
                                className="flex-1 text-center py-2 rounded-full text-sm font-semibold text-white"
                                style={{
                                    background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3))',
                                    border: '1px solid rgba(99,102,241,0.5)',
                                }}
                            >
                                Login
                            </div>
                        </motion.div>

                        {/* Messages */}
                        <AnimatePresence>
                            {registeredMessage && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10, height: 0 }}
                                    animate={{ opacity: 1, y: 0, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="text-green-300 text-sm text-center mb-4 px-3 py-2 rounded-xl"
                                    style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.25)' }}
                                >
                                    {registeredMessage}
                                </motion.div>
                            )}
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10, height: 0 }}
                                    animate={{ opacity: 1, y: 0, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="text-red-300 text-sm text-center mb-4 px-3 py-2 rounded-xl"
                                    style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)' }}
                                >
                                    {error}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* Username */}
                            <motion.div
                                initial={{ opacity: 0, x: -15 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.5 }}
                            >
                                <div
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${focusedField === 'username' ? 'input-focused' : ''}`}
                                    style={{
                                        background: focusedField === 'username' ? 'rgba(99,102,241,0.07)' : 'rgba(30,35,54,0.6)',
                                        border: `1px solid ${focusedField === 'username' ? 'rgba(99,102,241,0.6)' : '#1e2336'}`,
                                    }}
                                >
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={focusedField === 'username' ? '#818cf8' : '#4b5563'} strokeWidth="2">
                                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                                    </svg>
                                    <input
                                        type="text"
                                        required
                                        placeholder="Username or Email"
                                        value={formData.username}
                                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                        onFocus={() => setFocusedField('username')}
                                        onBlur={() => setFocusedField(null)}
                                        className="flex-1 bg-transparent text-white text-sm placeholder-gray-600 outline-none"
                                    />
                                </div>
                            </motion.div>

                            {/* Password */}
                            <motion.div
                                initial={{ opacity: 0, x: -15 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.6 }}
                            >
                                <div
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${focusedField === 'password' ? 'input-focused' : ''}`}
                                    style={{
                                        background: focusedField === 'password' ? 'rgba(99,102,241,0.07)' : 'rgba(30,35,54,0.6)',
                                        border: `1px solid ${focusedField === 'password' ? 'rgba(99,102,241,0.6)' : '#1e2336'}`,
                                    }}
                                >
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={focusedField === 'password' ? '#818cf8' : '#4b5563'} strokeWidth="2">
                                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                                    </svg>
                                    <input
                                        type="password"
                                        required
                                        placeholder="Password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        onFocus={() => setFocusedField('password')}
                                        onBlur={() => setFocusedField(null)}
                                        className="flex-1 bg-transparent text-white text-sm placeholder-gray-600 outline-none"
                                    />
                                </div>
                            </motion.div>

                            {/* Submit */}
                            <motion.div
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.7 }}
                            >
                                <motion.button
                                    type="submit"
                                    disabled={loading}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.97 }}
                                    className="w-full py-3.5 rounded-xl text-white font-bold text-sm btn-shine relative overflow-hidden disabled:opacity-60 disabled:cursor-not-allowed"
                                    style={{
                                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                                        boxShadow: '0 4px 24px rgba(99,102,241,0.35)',
                                    }}
                                >
                                    {loading ? (
                                        <span className="flex items-center justify-center gap-2">
                                            <motion.span
                                                className="w-4 h-4 border-2 border-white border-t-transparent rounded-full inline-block"
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                                            />
                                            Logging in...
                                        </span>
                                    ) : (
                                        'Login →'
                                    )}
                                </motion.button>
                            </motion.div>
                        </form>

                        {/* Footer */}
                        <motion.div
                            className="mt-6 pt-5 border-t flex items-center justify-between"
                            style={{ borderColor: '#1e2336' }}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.9 }}
                        >
                            <p className="text-gray-500 text-xs">
                                New here?{' '}
                                <Link
                                    href="/signup"
                                    className="font-semibold transition-colors"
                                    style={{ color: '#818cf8' }}
                                    onMouseEnter={(e) => (e.currentTarget.style.color = '#a5b4fc')}
                                    onMouseLeave={(e) => (e.currentTarget.style.color = '#818cf8')}
                                >
                                    Create an account
                                </Link>
                                {' '}— it's free.
                            </p>
                            <div className="flex -space-x-2">
                                {['🤖', '😺', '👾'].map((emoji, i) => (
                                    <div
                                        key={i}
                                        className="w-7 h-7 rounded-full flex items-center justify-center text-sm border-2"
                                        style={{ background: 'rgba(30,35,54,0.9)', borderColor: '#0f111a' }}
                                    >
                                        {emoji}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
