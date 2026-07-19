"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Ghost, Cpu, HardDrive, Clock, BrainCircuit } from "lucide-react";

interface PulseData {
    cpu: number;
    memory: number;
    idle: number;
    thought: string;
    is_speaking: boolean;
    is_listening: boolean;
    timestamp: number;
}

export default function SystemHUD() {
    const [ghostMode, setGhostMode] = useState(false);
    const [expanded, setExpanded] = useState(false);
    const [pulse, setPulse] = useState<PulseData | null>(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        let ws: WebSocket;
        let reconnectTimer: NodeJS.Timeout;

        const connectWS = () => {
            ws = new WebSocket("ws://localhost:8000/ws/pulse");

            ws.onopen = () => {
                setConnected(true);
                console.log("Connected to Pulse Engine");
            };

            ws.onmessage = (event) => {
                try {
                    const data: PulseData = JSON.parse(event.data);
                    setPulse(data);
                } catch (err) {
                    console.error("Failed to parse pulse data:", err);
                }
            };

            ws.onclose = () => {
                setConnected(false);
                reconnectTimer = setTimeout(connectWS, 3000);
            };

            ws.onerror = (err) => {
                // Silencing noisy error logs when backend is simply offline
                if (connected) {
                    console.warn("Pulse WebSocket disconnected unexpectedly.");
                }
                ws.close();
            };
        };

        connectWS();

        return () => {
            if (ws) ws.close();
            if (reconnectTimer) clearTimeout(reconnectTimer);
        };
    }, []);

    return (
        <div className="fixed top-6 right-6 z-50 flex flex-col items-end gap-3 pointer-events-none">

            {/* Ghost Mode Toggle */}
            <motion.button
                type="button"
                onClick={async () => {
                    const nextMode = !ghostMode;
                    setGhostMode(nextMode);
                    try {
                        await fetch(`http://localhost:8000/pulse/stealth?active=${nextMode}`, { method: 'POST' });
                    } catch (e) { console.error("Ghost sync failed", e); }
                }}
                className={`pointer-events-auto flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-mono backdrop-blur-md transition-all duration-300 ${ghostMode
                    ? "border-green-500/50 bg-green-500/10 text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]"
                    : "border-white/10 bg-black/40 text-white/40 hover:bg-white/10"
                    }`}
            >
                <Ghost size={14} className={ghostMode ? "animate-pulse" : ""} />
                <span>GHOST MODE {ghostMode ? "ON" : "OFF"}</span>
            </motion.button>

            {/* Thinking Graph (Pulse) */}
            <AnimatePresence>
                {!ghostMode && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        onMouseEnter={() => setExpanded(true)}
                        onMouseLeave={() => setExpanded(false)}
                        className="pointer-events-auto bg-black/50 border border-white/10 backdrop-blur-xl rounded-xl p-3 flex flex-col items-start min-w-[200px]"
                    >
                        <div className="flex items-center gap-2 w-full border-b border-white/10 pb-2 mb-3 relative">
                            <div className="relative">
                                <Activity size={14} className={`${connected ? (pulse?.is_listening ? "text-green-400 scale-125 transition-transform" : "text-blue-400 animate-pulse") : "text-red-500"}`} />
                                {pulse?.is_listening && (
                                    <motion.div
                                        layoutId="listening-glow"
                                        className="absolute inset-0 rounded-full bg-green-400/30 blur-sm scale-150"
                                        animate={{ opacity: [0.2, 0.5, 0.2] }}
                                        transition={{ duration: 1.5, repeat: Infinity }}
                                    />
                                )}
                            </div>
                            <span className="text-[10px] font-mono tracking-widest text-white/70 uppercase font-bold">
                                {connected ? (pulse?.is_speaking ? "NIA Speaking..." : "Sovereign Pulse Active") : "Pulse Disconnected"}
                            </span>
                        </div>

                        <div className="flex flex-col gap-3 w-full">
                            {/* Resource Metrics */}
                            <div className="grid grid-cols-2 gap-2 w-full">
                                <div className="flex items-center gap-2 bg-white/5 rounded-lg p-2 border border-white/5">
                                    <Cpu size={12} className="text-purple-400" />
                                    <div className="flex flex-col">
                                        <span className="text-[8px] text-white/40 uppercase">CPU</span>
                                        <span className="text-[10px] font-mono">{pulse?.cpu.toFixed(1) || "0.0"}%</span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 bg-white/5 rounded-lg p-2 border border-white/5">
                                    <HardDrive size={12} className="text-blue-400" />
                                    <div className="flex flex-col">
                                        <span className="text-[8px] text-white/40 uppercase">RAM</span>
                                        <span className="text-[10px] font-mono">{pulse?.memory.toFixed(1) || "0.0"}%</span>
                                    </div>
                                </div>
                            </div>

                            {/* Idle Time */}
                            <div className="flex items-center gap-3 bg-white/5 rounded-lg p-2 border border-white/5 w-full">
                                <Clock size={12} className="text-green-400" />
                                <div className="flex flex-col">
                                    <span className="text-[8px] text-white/40 uppercase">Global Idle</span>
                                    <span className="text-[10px] font-mono">{pulse?.idle || 0}s</span>
                                </div>
                            </div>

                            {/* Thought Stream */}
                            <div className="mt-1 flex flex-col gap-1.5 w-full">
                                <div className="flex items-center gap-1.5">
                                    <BrainCircuit size={12} className="text-pink-400" />
                                    <span className="text-[9px] font-mono text-white/60 uppercase">Trajectory</span>
                                </div>
                                <div className="p-2 rounded-lg bg-black/40 border border-white/5 min-h-[40px]">
                                    <p className="text-[9px] font-mono text-white/80 leading-relaxed italic">
                                        "{pulse?.thought || "Monitoring system states..."}"
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
