"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Terminal, Camera, Activity, Cpu } from "lucide-react";

export default function AgentConsole() {
    const [logs, setLogs] = useState([
        { type: "info", message: "NIA Agency Core Initializing..." },
        { type: "success", message: "Vision System: ONLINE" },
        { type: "success", message: "Action Loop: READY" },
    ]);

    return (
        <div className="flex-1 flex flex-col gap-6 p-8 bg-[#020202] text-white font-mono overflow-hidden">
            {/* Header Stats */}
            <div className="grid grid-cols-4 gap-4">
                {[
                    { label: "Brain", value: "Gemini 1.5", icon: Cpu, color: "text-blue-400" },
                    { label: "Vision", value: "Active", icon: Camera, color: "text-purple-400" },
                    { label: "Status", value: "Listening", icon: Activity, color: "text-green-400" },
                    { label: "Uptime", value: "99.9%", icon: Terminal, color: "text-yellow-400" },
                ].map((stat, i) => (
                    <div key={i} className="bg-white/5 border border-white/10 p-4 rounded-2xl flex items-center gap-4">
                        <stat.icon className={stat.color} size={20} />
                        <div>
                            <p className="text-[10px] text-white/30 uppercase tracking-widest">{stat.label}</p>
                            <p className="text-sm font-bold">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Main Console Area */}
            <div className="flex-1 grid grid-cols-3 gap-6 min-h-0">
                {/* Live Logs */}
                <div className="col-span-2 bg-[#050505] border border-white/10 rounded-2xl p-6 flex flex-col overflow-hidden">
                    <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-4">
                        <div className="flex items-center gap-2">
                            <Terminal size={16} className="text-blue-400" />
                            <span className="text-xs uppercase tracking-widest text-white/50">Core Execution Log</span>
                        </div>
                        <div className="flex gap-1">
                            <div className="w-2 h-2 rounded-full bg-red-500/50" />
                            <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                            <div className="w-2 h-2 rounded-full bg-green-500/50" />
                        </div>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-2 text-[12px]">
                        {logs.map((log, i) => (
                            <div key={i} className="flex gap-4">
                                <span className={log.type === "success" ? "text-green-400" : "text-blue-400"}>
                                    [{new Date().toLocaleTimeString()}]
                                </span>
                                <span className="text-white/80">{log.message}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Perspective (Camera/Screen Preview Placeholder) */}
                <div className="flex flex-col gap-6">
                    <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5" />
                        <div className="absolute top-4 left-4 flex items-center gap-2">
                            <Camera size={14} className="text-purple-400" />
                            <span className="text-[10px] uppercase tracking-widest text-white/30 font-bold">Live Perspective</span>
                        </div>
                        <div className="h-full flex items-center justify-center">
                            <p className="text-xs text-white/20 uppercase tracking-[0.2em]">Visual Stream Encrypted</p>
                        </div>
                    </div>

                    <div className="h-48 bg-white/5 border border-white/10 rounded-2xl p-6">
                        <span className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-4 block">Action Queue</span>
                        <div className="space-y-3">
                            <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: "60%" }}
                                    className="h-full bg-blue-500"
                                />
                            </div>
                            <p className="text-[10px] text-white/40">Analyzing goal: "Organize downloads folder"</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
