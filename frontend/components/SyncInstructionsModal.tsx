import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Download,
    FolderOpen,
    Settings,
    ToggleRight,
    Blocks,
    RefreshCw,
    X,
    ChevronRight,
    ChevronLeft,
    Youtube
} from 'lucide-react';

interface SyncInstructionsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const STEPS = [
    {
        id: 1,
        title: 'Download Extension',
        icon: <Download size={24} className="text-indigo-400" />,
        description: 'Download the compiled extension ZIP file containing the smart sync tools.',
        actionText: 'Download ZIP',
        actionLink: 'https://github.com/your-repo/releases/latest', // Replace with real link
        note: 'Save this file somewhere easy to find, like your Downloads or Desktop folder.'
    },
    {
        id: 2,
        title: 'Extract the Folder',
        icon: <FolderOpen size={24} className="text-indigo-400" />,
        description: 'Find the ZIP file you just downloaded, right-click it, and select "Extract All".',
        note: 'Do not delete this extracted folder later, Chrome reads the extension directly from it.'
    },
    {
        id: 3,
        title: 'Open Extension Settings',
        icon: <Settings size={24} className="text-indigo-400" />,
        description: 'Open a new tab in Chrome and type the following address into your URL bar:',
        codeSnippet: 'chrome://extensions/',
    },
    {
        id: 4,
        title: 'Enable Developer Mode',
        icon: <ToggleRight size={24} className="text-indigo-400" />,
        description: 'Look at the top-right corner of the Extensions page and turn on the "Developer mode" toggle switch.',
    },
    {
        id: 5,
        title: 'Load Unpacked',
        icon: <Blocks size={24} className="text-indigo-400" />,
        description: 'A new menu bar will appear at the top. Click the "Load unpacked" button and select the folder you extracted in Step 2.',
        note: 'Make sure you select the specific folder that contains the manifest.json file.'
    },
    {
        id: 6,
        title: 'Start Syncing!',
        icon: <RefreshCw size={24} className="text-indigo-400" />,
        description: 'Pin the new extension to your toolbar. Go to youtube.com/playlist?list=WL, click the extension icon, and hit Sync!',
        note: 'The AI will organize your watch later videos into smart, categorized playlists here on your dashboard.'
    }
];

export default function SyncInstructionsModal({ isOpen, onClose }: SyncInstructionsModalProps) {
    const [currentStep, setCurrentStep] = useState(0);

    if (!isOpen) return null;

    const nextStep = () => {
        if (currentStep < STEPS.length - 1) setCurrentStep(c => c + 1);
    };

    const prevStep = () => {
        if (currentStep > 0) setCurrentStep(c => c - 1);
    };

    const activeStep = STEPS[currentStep];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="relative w-full max-w-2xl rounded-2xl border shadow-2xl overflow-hidden flex flex-col"
                style={{ background: '#0f111a', borderColor: '#2a3050' }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b" style={{ borderColor: '#2a3050' }}>
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-xl" style={{ background: 'rgba(99,102,241,0.1)' }}>
                            <Youtube size={20} className="text-indigo-400" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white">How to Sync Watch Later</h2>
                            <p className="text-sm text-gray-400">Step {currentStep + 1} of {STEPS.length}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content Area */}
                <div className="flex-1 p-8 min-h-[320px] flex flex-col justify-center relative overflow-hidden" style={{ background: '#131623' }}>
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.2 }}
                            className="flex flex-col items-center text-center max-w-lg mx-auto"
                        >
                            <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6" style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)' }}>
                                {activeStep.icon}
                            </div>

                            <h3 className="text-2xl font-semibold text-white mb-3">
                                {activeStep.title}
                            </h3>

                            <p className="text-gray-300 text-lg leading-relaxed mb-6">
                                {activeStep.description}
                            </p>

                            {activeStep.codeSnippet && (
                                <div className="px-4 py-3 rounded-lg text-indigo-300 font-mono text-sm mb-6 border w-full text-center select-all" style={{ background: '#0f111a', borderColor: '#2a3050' }}>
                                    {activeStep.codeSnippet}
                                </div>
                            )}

                            {activeStep.actionText && activeStep.actionLink && (
                                <a
                                    href={activeStep.actionLink}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="mb-6 px-6 py-3 rounded-full text-white font-medium shadow-lg hover:shadow-indigo-500/25 transition-all transform hover:-translate-y-0.5"
                                    style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                                >
                                    {activeStep.actionText}
                                </a>
                            )}

                            {activeStep.note && (
                                <div className="mt-auto px-4 py-3 rounded-lg border text-sm text-gray-400 w-full flex gap-3 text-left items-start" style={{ background: 'rgba(255,255,255,0.02)', borderColor: '#2a3050' }}>
                                    <div className="text-indigo-400 mt-0.5">ⓘ</div>
                                    <p>{activeStep.note}</p>
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Footer / Navigation */}
                <div className="p-6 border-t flex items-center justify-between" style={{ borderColor: '#2a3050', background: '#0f111a' }}>

                    {/* Progress dots */}
                    <div className="flex gap-2">
                        {STEPS.map((_, i) => (
                            <div
                                key={i}
                                className={`h-2 rounded-full transition-all duration-300 ${i === currentStep ? 'w-6' : 'w-2'}`}
                                style={{ background: i === currentStep ? '#818cf8' : '#2a3050' }}
                            />
                        ))}
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3">
                        <button
                            onClick={prevStep}
                            disabled={currentStep === 0}
                            className="px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
                            style={{ color: '#9ca3af', border: '1px solid #2a3050' }}
                        >
                            <ChevronLeft size={16} />
                            Back
                        </button>
                        <button
                            onClick={currentStep === STEPS.length - 1 ? onClose : nextStep}
                            className="px-6 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 text-white shadow-lg"
                            style={{ background: currentStep === STEPS.length - 1 ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                        >
                            {currentStep === STEPS.length - 1 ? 'Done' : 'Next'}
                            {currentStep !== STEPS.length - 1 && <ChevronRight size={16} />}
                        </button>
                    </div>

                </div>
            </motion.div>
        </div>
    );
}
