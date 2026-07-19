"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, ShieldCheck, Volume2, Cpu } from "lucide-react";

interface SoulState {
  label: string;
  status: "ONLINE" | "OFFLINE" | "INITIALIZING";
  icon: any;
  color: string;
}

export default function SoulStatus() {
  const [souls, setSouls] = useState<SoulState[]>([
    { label: "Executive Soul", status: "INITIALIZING", icon: ShieldCheck, color: "text-blue-400" },
    { label: "Pulse Soul", status: "INITIALIZING", icon: Cpu, color: "text-purple-400" },
    { label: "Vocal Soul", status: "INITIALIZING", icon: Volume2, color: "text-green-400" },
  ]);

  useEffect(() => {
    const checkSouls = async () => {
      try {
        // Check Pulse Soul (API)
        const res = await fetch("http://127.0.0.1:8000/", { mode: 'no-cors' });
        // Since we use no-cors, we can't see the body, but if it doesn't throw, it's likely up
        
        setSouls(prev => prev.map(s => {
          if (s.label === "Pulse Soul") return { ...s, status: "ONLINE" };
          if (s.label === "Executive Soul") return { ...s, status: "ONLINE" }; // Frontend is here
          return s;
        }));
      } catch (e) {
        setSouls(prev => prev.map(s => {
          if (s.label === "Pulse Soul") return { ...s, status: "OFFLINE" };
          return s;
        }));
      }

      // Check Vocal Soul (optional check for pipecat bridge)
      try {
        const res = await fetch("http://127.0.0.1:8000/pulse/chat", { 
          method: 'POST', 
          body: JSON.stringify({ prompt: "ping" }),
          headers: { "Content-Type": "application/json" }
        });
        if (res.ok) {
           setSouls(prev => prev.map(s => s.label === "Vocal Soul" ? { ...s, status: "ONLINE" } : s));
        }
      } catch (e) {}
    };

    const interval = setInterval(checkSouls, 5000);
    checkSouls();
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      {souls.map((soul, i) => (
        <motion.div
          key={soul.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xl relative overflow-hidden group"
        >
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
            <soul.icon size={40} className={soul.color} />
          </div>
          
          <div className="flex items-center gap-3 mb-3">
            <div className={`w-2 h-2 rounded-full animate-pulse ${soul.status === "ONLINE" ? "bg-green-500" : soul.status === "OFFLINE" ? "bg-red-500" : "bg-yellow-500"}`} />
            <span className="text-[10px] uppercase tracking-[0.2em] font-mono text-white/40">{soul.label}</span>
          </div>
          
          <p className={`text-xl font-bold tracking-tight ${soul.color}`}>{soul.status}</p>
          <div className="mt-4 h-1 w-full bg-white/5 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: soul.status === "ONLINE" ? "100%" : "0%" }}
              className={`h-full bg-gradient-to-r from-transparent via-${soul.color.split('-')[1]}-500 to-transparent`}
              transition={{ duration: 1 }}
            />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
