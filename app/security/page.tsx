"use client";

import React, { useState } from "react";
import InnerLayout from "@/components/layouts/InnerLayout";
import { motion } from "framer-motion";
import { 
  ShieldCheck, Lock, Eye, EyeOff, AlertTriangle, CheckCircle2, 
  KeyRound, Fingerprint, Globe, Network, RefreshCw
} from "lucide-react";

function StatusRow({ icon: Icon, label, status, detail, ok }: any) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-none">
      <div className="flex items-center gap-3">
        <Icon size={15} className={ok ? "text-green-400" : "text-orange-400"} />
        <div>
          <p className="text-sm text-white/80">{label}</p>
          <p className="text-[11px] font-mono text-white/30">{detail}</p>
        </div>
      </div>
      <span className={`flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded-full border ${ok ? "border-green-500/30 bg-green-500/10 text-green-400" : "border-orange-500/30 bg-orange-500/10 text-orange-400"}`}>
        {ok ? <CheckCircle2 size={10} /> : <AlertTriangle size={10} />}
        {status}
      </span>
    </div>
  );
}

function ToggleRow({ label, desc, value, onChange }: any) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-none">
      <div>
        <p className="text-sm text-white/80">{label}</p>
        <p className="text-[11px] font-mono text-white/30">{desc}</p>
      </div>
      <button
        onClick={() => onChange(!value)}
        className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${value ? "bg-blue-600" : "bg-white/10"}`}
      >
        <motion.div
          animate={{ x: value ? 22 : 2 }}
          transition={{ type: "spring", damping: 18, stiffness: 250 }}
          className="absolute top-1 w-4 h-4 rounded-full bg-white shadow"
        />
      </button>
    </div>
  );
}

export default function SecurityPage() {
  const [settings, setSettings] = useState({
    ghostMode: false,
    encryptMemory: true,
    localOnlyMode: false,
    screenLock: true,
    auditLog: true,
  });

  const toggle = (key: keyof typeof settings) => setSettings(s => ({ ...s, [key]: !s[key] }));

  return (
    <InnerLayout>
      <div className="min-h-screen bg-black text-white px-8 py-10 overflow-y-auto custom-scrollbar">
      {/* Header */}
      <div className="mb-10">
        <p className="text-[11px] uppercase tracking-[0.3em] font-mono text-white/30">Sovereign Integrity</p>
        <h1 className="text-3xl font-semibold mt-1">Security</h1>
        <p className="text-white/40 text-sm mt-1">Active threat surface and privacy controls</p>
      </div>

      {/* Security Score */}
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-br from-blue-900/30 to-purple-900/20 border border-blue-500/20 rounded-2xl p-6 mb-8 flex items-center gap-6"
      >
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
            <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
            <circle cx="40" cy="40" r="34" fill="none" stroke="#3b82f6" strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 34 * 0.82} ${2 * Math.PI * 34}`} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg font-bold text-blue-400">82</span>
          </div>
        </div>
        <div>
          <p className="text-lg font-semibold text-white/90">Security Score: Good</p>
          <p className="text-sm text-white/40 mt-1">Enable Ghost Mode and Local-Only to reach 100%</p>
          <div className="flex gap-2 mt-3">
            <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-green-400">3 Passed</span>
            <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400">2 Warnings</span>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Status */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck size={14} className="text-white/40" />
            <span className="text-[11px] uppercase tracking-widest font-mono text-white/40">System Status</span>
          </div>
          <StatusRow icon={Lock} label="Memory Encryption" detail="AES-256 at rest" status="Active" ok={true} />
          <StatusRow icon={Network} label="API Transmission" detail="TLS 1.3 enforced" status="Secured" ok={true} />
          <StatusRow icon={Fingerprint} label="Identity Layer" detail="Sovereign binding active" status="Bound" ok={true} />
          <StatusRow icon={Globe} label="Ghost Mode" detail="Hides NIA from OS processes" status="Inactive" ok={false} />
          <StatusRow icon={KeyRound} label="Local-Only Mode" detail="Blocks all external API calls" status="Disabled" ok={false} />
        </div>

        {/* Privacy Controls */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md">
          <div className="flex items-center gap-2 mb-4">
            <Eye size={14} className="text-white/40" />
            <span className="text-[11px] uppercase tracking-widest font-mono text-white/40">Privacy Controls</span>
          </div>
          <ToggleRow label="Ghost Mode" desc="Hides NIA from task managers" value={settings.ghostMode} onChange={() => toggle("ghostMode")} />
          <ToggleRow label="Encrypt Memory Bank" desc="AES encrypt stored memories" value={settings.encryptMemory} onChange={() => toggle("encryptMemory")} />
          <ToggleRow label="Local-Only Mode" desc="Disable all cloud AI providers" value={settings.localOnlyMode} onChange={() => toggle("localOnlyMode")} />
          <ToggleRow label="Screen Lock on Idle" desc="Auto-lock after 10 min idle" value={settings.screenLock} onChange={() => toggle("screenLock")} />
          <ToggleRow label="Audit Log" desc="Record all NIA actions" value={settings.auditLog} onChange={() => toggle("auditLog")} />
        </div>
      </div>
      </div>
    </InnerLayout>
  );
}
