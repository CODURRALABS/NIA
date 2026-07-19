"use client";

import { useState, useEffect } from "react";
import { Mic, MicOff, Code2, Send, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useSearchParams } from "next/navigation";

interface CommandBarProps {
    onCommand: (cmd: string) => void;
    isProcessing?: boolean;
}

export default function CommandBar({ onCommand, isProcessing = false }: CommandBarProps) {
    const [command, setCommand] = useState("");
    const [voiceActive, setVoiceActive] = useState(false);
    const [vibeMode, setVibeMode] = useState(false);
    const searchParams = useSearchParams();

    useEffect(() => {
        if (searchParams.get("voice") === "true") {
            setVoiceActive(true);
        }
    }, [searchParams]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!command.trim() || isProcessing) return;

        onCommand(command);
        setCommand("");
    };

    return (
        <div className="w-full border-t border-white/10 bg-[#050505]/90 backdrop-blur-xl px-6 py-4">
            <form onSubmit={handleSubmit} className="flex items-center gap-3 max-w-screen-2xl mx-auto">

                {/* Vibe Coding Toggle */}
                <motion.button
                    type="button"
                    onClick={() => setVibeMode(!vibeMode)}
                    whileTap={{ scale: 0.92 }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full border text-xs font-mono uppercase tracking-wider transition-all duration-300 ${vibeMode
                        ? "border-purple-500 bg-purple-500/20 text-purple-300"
                        : "border-white/20 text-white/40 hover:border-white/40"
                        }`}
                >
                    <Code2 size={14} />
                    <span className="hidden sm:inline">Vibe</span>
                </motion.button>

                {/* Command Input */}
                <div className="flex-1 relative">
                    <input
                        type="text"
                        value={command}
                        onChange={(e) => setCommand(e.target.value)}
                        placeholder={vibeMode ? "Describe what to build... NIA will vibe-code it." : "Give NIA a sovereign command..."}
                        className="w-full bg-white/5 border border-white/10 rounded-full px-5 py-2.5 text-sm text-white/80 placeholder-white/25 font-mono focus:outline-none focus:border-blue-500/50 focus:bg-white/8 transition-all duration-300"
                    />
                    <AnimatePresence>
                        {vibeMode && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="absolute right-4 top-1/2 -translate-y-1/2"
                            >
                                <Zap size={14} className="text-purple-400 animate-pulse" />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Send Button */}
                <motion.button
                    type="submit"
                    whileTap={{ scale: 0.92 }}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-blue-600/80 hover:bg-blue-500 border-none text-white text-xs font-mono uppercase tracking-wider transition-all duration-300"
                >
                    <Send size={14} />
                    <span className="hidden sm:inline">Execute</span>
                </motion.button>

                {/* Voice Interruption Toggle */}
                <motion.button
                    type="button"
                    onClick={() => setVoiceActive(!voiceActive)}
                    whileTap={{ scale: 0.92 }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full border text-xs font-mono uppercase tracking-wider transition-all duration-300 ${voiceActive
                        ? "border-red-500 bg-red-500/20 text-red-300"
                        : "border-white/20 text-white/40 hover:border-white/40"
                        }`}
                >
                    {voiceActive ? <Mic size={14} className="animate-pulse" /> : <MicOff size={14} />}
                    <span className="hidden sm:inline">{voiceActive ? "Listening" : "Voice"}</span>
                </motion.button>

            </form>
        </div>
    );
}
