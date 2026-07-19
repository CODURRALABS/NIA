"use client";

import React, { useState, useEffect } from "react";
import InnerLayout from "@/components/layouts/InnerLayout";
import { motion } from "framer-motion";
import { 
  Cpu, HardDrive, Activity, Zap, Globe, ShieldCheck, 
  BrainCircuit, BarChart3, Clock, TrendingUp, Wifi, ZapOff
} from "lucide-react";
import SoulStatus from "@/components/SoulStatus";
import ProactiveHub from "@/components/ProactiveHub";

function MetricCard({ icon: Icon, label, value, unit, color, percent }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col gap-3 backdrop-blur-md"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon size={16} className={color} />
          <span className="text-[11px] uppercase tracking-widest font-mono text-white/50">{label}</span>
        </div>
        <span className={`text-xs font-mono font-bold ${color}`}>{value}<span className="text-white/30 text-[10px]"> {unit}</span></span>
      </div>
      <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r ${color.includes("blue") ? "from-blue-600 to-blue-400" : color.includes("purple") ? "from-purple-600 to-purple-400" : color.includes("green") ? "from-green-600 to-green-400" : "from-orange-600 to-orange-400"}`}
        />
      </div>
    </motion.div>
  );
}

const activities = [
  { time: "Just now", event: "Vision analysis cycle completed", type: "vision" },
  { time: "2m ago", event: "Groq Llama-3 responded in 312ms", type: "ai" },
  { time: "5m ago", event: "User opened Sovereign Hub", type: "system" },
  { time: "11m ago", event: "Pulse Engine synced with frontend", type: "system" },
  { time: "18m ago", event: "Memory checkpoint saved", type: "memory" },
  { time: "32m ago", event: "Session initialized", type: "system" },
];

const typeColor: Record<string, string> = {
  vision: "text-blue-400",
  ai: "text-purple-400",
  system: "text-white/50",
  memory: "text-green-400",
};

export default function DashboardPage() {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setTick(p => p + 1), 2000);
    return () => clearInterval(t);
  }, []);

  const cpuVal = (35 + Math.sin(tick * 0.4) * 15).toFixed(1);
  const ramVal = (62 + Math.cos(tick * 0.3) * 5).toFixed(1);
  const netVal = (4.2 + Math.sin(tick * 0.6) * 1.8).toFixed(1);

  return (
    <InnerLayout>
      <div className="min-h-screen bg-black text-white px-8 py-10 overflow-y-auto custom-scrollbar">
        {/* Header */}
        <div className="mb-10 flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-[0.3em] font-mono text-white/30">Sovereign Overview</p>
            <h1 className="text-3xl font-semibold mt-1 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">System Dashboard</h1>
            <p className="text-white/40 text-sm mt-1">Real-time system metrics and NIA activity feed</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-mono text-white/20 uppercase tracking-widest">Network Mode</span>
              <span className="text-xs font-mono text-blue-400">SOVEREIGN_OFFLINE</span>
            </div>
            <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
              <ShieldCheck size={18} className="text-blue-400" />
            </div>
          </div>
        </div>

        {/* Real-time Soul Status */}
        <SoulStatus />

        {/* Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard icon={Cpu} label="CPU Load" value={cpuVal} unit="%" color="text-blue-400" percent={parseFloat(cpuVal)} />
          <MetricCard icon={HardDrive} label="RAM Usage" value={ramVal} unit="%" color="text-purple-400" percent={parseFloat(ramVal)} />
          <MetricCard icon={Wifi} label="Network" value={netVal} unit="MB/s" color="text-green-400" percent={parseFloat(netVal) * 8} />
          <MetricCard icon={Zap} label="AI Latency" value="312" unit="ms" color="text-orange-400" percent={31} />
        </div>

        {/* Status Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Brain Providers", value: "3 Active", icon: BrainCircuit, color: "text-purple-400", sub: "Groq · Gemini · HuggingFace" },
            { label: "Vision Engine", value: "Online", icon: Activity, color: "text-green-400", sub: "Gemini 1.5 Flash Multimodal" },
            { label: "Voice Engine", value: "Active", icon: Globe, color: "text-blue-400", sub: "Sarvam Bulbul v3 · Ritu Voice" },
          ].map((card) => (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-md"
            >
              <div className="flex items-center gap-2 mb-1">
                <card.icon size={15} className={card.color} />
                <span className="text-[10px] uppercase tracking-widest font-mono text-white/40">{card.label}</span>
              </div>
              <p className={`text-lg font-semibold ${card.color}`}>{card.value}</p>
              <p className="text-white/30 text-xs mt-0.5 font-mono">{card.sub}</p>
            </motion.div>
          ))}
        </div>

        {/* Activity Log */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md">
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 size={14} className="text-white/40" />
            <span className="text-[11px] uppercase tracking-widest font-mono text-white/40">Activity Feed</span>
          </div>
          <div className="flex flex-col gap-3">
            {activities.map((a, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="flex items-center gap-4 border-b border-white/5 pb-3 last:border-none last:pb-0"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-white/20 flex-shrink-0" />
                <span className={`text-xs font-mono flex-1 ${typeColor[a.type]}`}>{a.event}</span>
                <span className="text-[10px] text-white/30 font-mono flex-shrink-0">{a.time}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Floating Interaction Hub */}
        <ProactiveHub />
      </div>
    </InnerLayout>
  );
}
