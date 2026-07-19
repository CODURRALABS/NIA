"use client";

import { useEffect, useState } from "react";

export default function SovereignMemory() {
    const [memoryState, setMemoryState] = useState<string[]>([]);

    // Simulate 12GB to 8GB binary memory compression visualization
    useEffect(() => {
        const generateBinaryRow = () => {
            return Array.from({ length: 16 }, () => Math.round(Math.random())).join("");
        };

        const interval = setInterval(() => {
            setMemoryState(prev => {
                const newRows = [...prev, generateBinaryRow()];
                if (newRows.length > 20) newRows.shift();
                return newRows;
            });
        }, 300);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="h-full w-full font-mono text-[10px] text-blue-400/60 leading-tight">
            <div className="mb-4 text-xs text-blue-300 font-bold border-b border-blue-900/50 pb-2">
                <span className="text-white">ACTIVE:</span> 8.4GB / 12.0GB (COMPRESSED)
            </div>
            <div className="flex flex-col opacity-70">
                {memoryState.map((row, i) => (
                    <div key={i} className="flex justify-between">
                        <span>0x{(0x1000 + i * 16).toString(16).toUpperCase()}</span>
                        <span className="tracking-[0.2em]">{row}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
