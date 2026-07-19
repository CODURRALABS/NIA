"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import {
    getNiaSettings,
    updateNiaSettings,
    NiaSettings
} from '@/lib/supabaseSettings';
import {
    User,
    Volume2,
    MessageSquare,
    Globe,
    Save,
    ArrowLeft,
    Play,
    CheckCircle2
} from 'lucide-react';

const SARVAM_VOICES = [
    { id: 'meera', name: 'Meera (Female)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'pavithra', name: 'Pavithra (Female)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'mahesh', name: 'Mahesh (Male)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'kumar', name: 'Kumar (Male)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'saranya', name: 'Saranya (Female)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'vignesh', name: 'Vignesh (Male)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'mishti', name: 'Mishti (Female)', lang: 'Hindi/Multi', provider: 'Sarvam' },
    { id: 'arvind', name: 'Arvind (Male)', lang: 'Hindi/Multi', provider: 'Sarvam' },
];

export default function PersonalizationPage() {
    const [settings, setSettings] = useState<NiaSettings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState(false);
    const [fromPortal, setFromPortal] = useState(false);
    const router = useRouter();

    useEffect(() => {
        if (typeof window !== 'undefined') {
            setFromPortal(window.location.search.includes('from_portal=true'));
        }
        const loadSettings = async () => {
            const data = await getNiaSettings('default_user');
            setSettings(data);
            setLoading(false);
        };
        loadSettings();
    }, []);

    const handleSave = async () => {
        if (!settings) return;
        setSaving(true);
        try {
            await updateNiaSettings('default_user', settings);
            setSuccess(true);
            if (fromPortal) {
                // Pre-play greeting right on user click to bypass Hub autoplay block
                try {
                    const text = settings.language === 'hi-IN' ? settings.greeting_hi : settings.greeting_en;
                    const res = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            text: text || "Hello boss",
                            speaker: settings.voice_id,
                            language_code: settings.language === 'hi-IN' ? 'hi-IN' : 'en-IN'
                        })
                    });
                    const data = await res.json();
                    if (data.audio) {
                        const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
                        audio.play().catch(e => console.warn("Audio play blocked", e));
                    }
                } catch (e) {
                    console.error("Auto Voice Failed", e);
                }

                setTimeout(() => router.push('/hub'), 1500);
            } else {
                setTimeout(() => setSuccess(false), 3000);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setSaving(false);
        }
    };

    const playSample = (voiceId: string) => {
        const audio = new Audio(`/audio/samples/${voiceId}.wav`);
        audio.play().catch(err => {
            console.warn(`Static sample for ${voiceId} not found, falling back to live preview`, err);
            previewVoice(voiceId);
        });
    };

    const previewVoice = async (voiceId: string) => {
        const text = settings?.language === 'hi-IN'
            ? settings.greeting_hi
            : settings?.greeting_en;

        try {
            const res = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text || "Hello",
                    speaker: voiceId,
                    language_code: settings?.language === 'hi-IN' ? 'hi-IN' : 'en-IN'
                })
            });
            const data = await res.json();
            if (data.audio) {
                const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
                audio.play();
            }
        } catch (err) {
            console.error("Preview failed", err);
        }
    };

    if (loading) return (
        <div className="min-h-screen bg-[#020202] flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans selection:bg-blue-500/30">
            {/* Background Glows */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full"></div>
            </div>

            <main className="relative z-10 max-w-5xl mx-auto px-6 py-12">
                {/* Header */}
                <div className="flex items-center justify-between mb-12">
                    <button
                        onClick={() => router.push('/hub')}
                        className="flex items-center gap-2 text-white/50 hover:text-white transition-colors group"
                    >
                        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                        <span className="font-mono text-sm uppercase tracking-widest">
                            {fromPortal ? "Enter Sovereign Hub" : "Back to Hub"}
                        </span>
                    </button>
                    <h1 className="text-3xl font-light tracking-[0.2em] uppercase">Personalization</h1>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                    {/* Left Column: Language & Persona */}
                    <div className="space-y-8">
                        {/* Persona Profile Card */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl"
                        >
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-3 shadow-lg shadow-blue-500/20">
                                    <User size={24} className="text-white" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-medium">Assistant Identity</h2>
                                    <p className="text-xs text-white/40 font-mono">SOVEREIGN CORE V2.5</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="group">
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">Assistant Name</label>
                                    <input
                                        type="text"
                                        value={settings?.persona_name}
                                        onChange={(e) => setSettings(s => s ? { ...s, persona_name: e.target.value } : null)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 transition-all"
                                    />
                                </div>
                                <div className="group">
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">Relationship Tone</label>
                                    <select
                                        value={settings?.relationship || "Companion"}
                                        onChange={(e) => setSettings(s => s ? { ...s, relationship: e.target.value } : null)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 transition-all appearance-none text-white/80"
                                    >
                                        <option value="Companion" className="bg-neutral-900">Companion (Warm & Casual)</option>
                                        <option value="Assistant" className="bg-neutral-900">Assistant (Professional & Focused)</option>
                                        <option value="Protective Sister" className="bg-neutral-900">Protective Sister (Caring & Direct)</option>
                                        <option value="Formal Operator" className="bg-neutral-900">Formal Operator (Strict & Objective)</option>
                                    </select>
                                </div>
                                <div className="group">
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">Custom Wake Word</label>
                                    <input
                                        type="text"
                                        placeholder="e.g. Nia"
                                        value={settings?.wake_word || "Nia"}
                                        onChange={(e) => setSettings(s => s ? { ...s, wake_word: e.target.value } : null)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 transition-all"
                                    />
                                </div>
                                <div className="group">
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">Primary Language</label>
                                    <div className="flex gap-2">
                                        {['en-IN', 'hi-IN'].map((lang) => (
                                            <button
                                                key={lang}
                                                onClick={() => setSettings(s => s ? { ...s, language: lang } : null)}
                                                className={`flex-1 py-2.5 rounded-xl border text-xs font-mono transition-all ${settings?.language === lang ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'}`}
                                            >
                                                {lang === 'en-IN' ? 'English (India)' : 'Hindi (India)'}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        {/* Greeting Settings */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl"
                        >
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center border border-green-500/20">
                                    <MessageSquare size={18} className="text-green-400" />
                                </div>
                                <h2 className="text-lg font-light tracking-wide">Greeting Messages</h2>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">English Greeting</label>
                                    <textarea
                                        rows={2}
                                        value={settings?.greeting_en}
                                        onChange={(e) => setSettings(s => s ? { ...s, greeting_en: e.target.value } : null)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] uppercase tracking-widest text-white/30 mb-2 ml-1">Hindi Greeting</label>
                                    <textarea
                                        rows={2}
                                        value={settings?.greeting_hi}
                                        onChange={(e) => setSettings(s => s ? { ...s, greeting_hi: e.target.value } : null)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm font-hindi focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Right Column: Voice Selection Carousel */}
                    <div className="flex flex-col h-full">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className="flex-1 p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl flex flex-col"
                        >
                            <div className="flex items-center justify-between mb-8">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                                        <Volume2 size={18} className="text-blue-400" />
                                    </div>
                                    <h2 className="text-lg font-light tracking-wide">Voice Profile</h2>
                                </div>
                                <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">SARVAM AI</span>
                            </div>

                            <div className="space-y-3 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar">
                                {SARVAM_VOICES.map((voice) => (
                                    <button
                                        key={voice.id}
                                        onClick={() => setSettings(s => s ? { ...s, voice_id: voice.id } : null)}
                                        className={`w-full group relative overflow-hidden p-4 rounded-2xl border transition-all text-left flex items-center justify-between gap-4 ${settings?.voice_id === voice.id
                                            ? 'bg-blue-500/10 border-blue-500/50 ring-1 ring-blue-500/30'
                                            : 'bg-white/5 border-white/10 hover:border-white/30'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${settings?.voice_id === voice.id ? 'bg-blue-500 text-white' : 'bg-white/10 text-white/40'}`}>
                                                <Volume2 size={14} />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium">{voice.name}</p>
                                                <p className="text-[10px] text-white/30 uppercase tracking-tighter">{voice.lang} • {voice.provider}</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <div
                                                onClick={(e) => { e.stopPropagation(); playSample(voice.id); }}
                                                className="flex items-center gap-2 group/play p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/60 hover:text-white transition-all active:scale-95"
                                            >
                                                <Play size={12} fill="currentColor" />
                                                <span className="text-[9px] uppercase tracking-tighter hidden group-hover/play:block px-1">Play Sample</span>
                                            </div>
                                            {settings?.voice_id === voice.id && (
                                                <motion.div layoutId="check" className="text-blue-400">
                                                    <CheckCircle2 size={18} />
                                                </motion.div>
                                            )}
                                        </div>
                                    </button>
                                ))}
                            </div>

                            <div className="mt-auto pt-8 flex items-center justify-between border-t border-white/5">
                                <p className="text-[10px] text-white/30 uppercase tracking-[0.2em] font-mono italic">Powered by Bulbul v3 Engine</p>
                                <button
                                    onClick={handleSave}
                                    disabled={saving}
                                    className={`px-8 py-3 rounded-2xl bg-white text-black font-semibold text-sm flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 hover:bg-blue-50 hover:shadow-lg hover:shadow-blue-500/10`}
                                >
                                    {saving ? <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></div> : <Save size={16} />}
                                    {saving ? 'Saving...' : (fromPortal ? 'Save & Enter Hub' : 'Save Settings')}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                </div>

                <AnimatePresence>
                    {success && (
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 50 }}
                            className="fixed bottom-12 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-6 py-3 rounded-full bg-green-500 text-white shadow-2xl shadow-green-500/40"
                        >
                            <CheckCircle2 size={18} />
                            <span className="text-sm font-medium">Settings Updated Successfully</span>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}
