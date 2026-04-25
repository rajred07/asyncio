'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { UsersService } from '@/lib/api/services/UsersService';
import { ApiError } from '@/lib/api/core/ApiError';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';

// --- Background Orbs matching app palette ---
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

// --- Hero Card ---
function HeroCard() {
    return (
        <motion.div
            className="relative"
            animate={{ rotateY: [0, 8, -8, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
            style={{ perspective: '1200px' }}
        >
            <motion.div
                className="absolute inset-0 rounded-2xl blur-2xl"
                style={{ background: 'rgba(99,102,241,0.4)', transform: 'scale(1.1)' }}
                animate={{ opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
            />
            <div
                className="relative w-72 rounded-2xl p-5 flex flex-col gap-4"
                style={{
                    background: 'rgba(15,17,26,0.9)',
                    border: '1px solid rgba(99,102,241,0.4)',
                    backdropFilter: 'blur(24px)',
                }}
            >
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

                <div
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium"
                    style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)' }}
                >
                    <span>✨</span>
                    <span className="text-indigo-300">AI sorted instantly</span>
                </div>

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

export default function SignupPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        full_name: '',
        username: '',
        email: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [focusedField, setFocusedField] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await UsersService.registerUserApiUsersRegisterPost({
                full_name: formData.full_name,
                username: formData.username,
                email: formData.email,
                password: formData.password,
            });
            router.push('/login?registered=true');
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.body?.detail || 'Registration failed');
            } else {
                setError('An unexpected error occurred');
            }
        } finally {
            setLoading(false);
        }
    };

    const fields = [
        {
            key: 'full_name',
            placeholder: 'Full Name',
            type: 'text',
            iconPath: <path d="M17 21v-2a4 4 0 0 0-3-3.87M9 21v-2a4 4 0 0 0-4-4v0a4 4 0 0 0-4 4v2M1 1l22 22" />,
            iconD: <><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></>,
        },
        {
            key: 'username',
            placeholder: 'Username',
            type: 'text',
        },
        {
            key: 'email',
            placeholder: 'Email',
            type: 'email',
        },
        {
            key: 'password',
            placeholder: 'Create Password',
            type: 'password',
        },
    ];

    const getIcon = (key: string, focused: boolean) => {
        const color = focused ? '#818cf8' : '#4b5563';
        const stroke = `stroke="${color}"`;
        if (key === 'full_name' || key === 'username') return (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
            </svg>
        );
        if (key === 'email') return (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
            </svg>
        );
        return (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
        );
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
                            <div
                                className="flex-1 text-center py-2 rounded-full text-sm font-semibold text-white"
                                style={{
                                    background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3))',
                                    border: '1px solid rgba(99,102,241,0.5)',
                                }}
                            >
                                Sign Up
                            </div>
                            <Link href="/login" className="flex-1">
                                <div className="text-center py-2 rounded-full text-sm font-medium text-gray-500 hover:text-gray-300 transition-colors cursor-pointer">
                                    Login
                                </div>
                            </Link>
                        </motion.div>

                        {/* Error */}
                        <AnimatePresence>
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

                        <form onSubmit={handleSubmit} className="space-y-3">
                            {fields.map((field, i) => (
                                <motion.div
                                    key={field.key}
                                    initial={{ opacity: 0, x: -15 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.45 + i * 0.08 }}
                                >
                                    <div
                                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${focusedField === field.key ? 'input-focused' : ''}`}
                                        style={{
                                            background: focusedField === field.key ? 'rgba(99,102,241,0.07)' : 'rgba(30,35,54,0.6)',
                                            border: `1px solid ${focusedField === field.key ? 'rgba(99,102,241,0.6)' : '#1e2336'}`,
                                        }}
                                    >
                                        {getIcon(field.key, focusedField === field.key)}
                                        <input
                                            type={field.type}
                                            required
                                            placeholder={field.placeholder}
                                            value={formData[field.key as keyof typeof formData]}
                                            onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
                                            onFocus={() => setFocusedField(field.key)}
                                            onBlur={() => setFocusedField(null)}
                                            className="flex-1 bg-transparent text-white text-sm placeholder-gray-600 outline-none"
                                        />
                                    </div>
                                </motion.div>
                            ))}

                            {/* Submit */}
                            <motion.div
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.82 }}
                                className="pt-1"
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
                                            Creating account...
                                        </span>
                                    ) : (
                                        'Start Curating →'
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
                            transition={{ delay: 1.0 }}
                        >
                            <div>
                                <p className="text-white text-xs font-semibold">Group Feature</p>
                                <p className="text-gray-500 text-xs mt-0.5">
                                    Already have an account?{' '}
                                    <Link
                                        href="/login"
                                        className="font-semibold transition-colors"
                                        style={{ color: '#818cf8' }}
                                        onMouseEnter={(e) => (e.currentTarget.style.color = '#a5b4fc')}
                                        onMouseLeave={(e) => (e.currentTarget.style.color = '#818cf8')}
                                    >
                                        Log in
                                    </Link>
                                </p>
                            </div>
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
