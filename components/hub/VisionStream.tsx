"use client";

import { useState, useEffect } from "react";
import { Terminal } from "lucide-react";

const mockLogs = [
    "[SYS] Initializing Sovereign Agency Module...",
    "[VISION] Scanning active viewport pixels.",
    "[MEMORY] Allocating 2GB RAM for contextual cache.",
    "[ACTION] Emulating mouse hover on element: 'SubmitBtn'.",
    "[VOICE] Ambient listening matrix engaged.",
    "[VIBE] Compiling abstract request into actionable UI update.",
    "...",
];

export default function VisionStream() {
    const [logs, setLogs] = useState<string[]>([]);

    useEffect(() => {
        let index = 0;
        const interval = setInterval(() => {
            if (index < mockLogs.length) {
                setLogs(prev => [...prev, mockLogs[index]]);
                index++;
            } else {
                // Recycle for visual effect
                setLogs([]);
                index = 0;
            }
        }, 1200);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="font-mono text-xs text-green-400/80 space-y-2">
            {logs.map((log, i) => (
                <div key={i} className="flex items-start space-x-2 animate-fade-in">
                    <Terminal size={12} className="mt-[2px] opacity-50 shrink-0" />
                    <span className="break-words">{log}</span>
                </div>
            ))}
            <div className="flex items-center space-x-2 opacity-50">
                <div className="w-1.5 h-3 bg-green-400 animate-pulse"></div>
            </div>
        </div>
    );
}
