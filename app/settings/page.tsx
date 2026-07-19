"use client";

import React, { useState } from "react";
import InnerLayout from "@/components/layouts/InnerLayout";
import { motion } from "framer-motion";
import { Settings, Sliders, Volume2, Eye, Globe, BrainCircuit, Palette, ChevronRight, Save, Check, Shield, Brain } from "lucide-react";

function Section({ title, icon: Icon, children }: any) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md mb-4">
      <div className="flex items-center gap-2 mb-5 pb-4 border-b border-white/10">
        <Icon size={14} className="text-white/40" />
        <span className="text-[11px] uppercase tracking-widest font-mono text-white/40">{title}</span>
      </div>
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

function SelectRow({ label, desc, options, value, onChange }: any) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-none">
      <div>
        <p className="text-sm text-white/80">{label}</p>
        <p className="text-[11px] font-mono text-white/30">{desc}</p>
      </div>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="bg-white/10 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white/70 outline-none focus:border-white/30 transition-colors cursor-pointer"
      >
        {options.map((o: string) => <option key={o} value={o} className="bg-neutral-900">{o}</option>)}
      </select>
    </div>
  );
}

function SliderRow({ label, desc, min, max, value, onChange, unit }: any) {
  return (
    <div className="flex flex-col gap-2 py-3 border-b border-white/5 last:border-none">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white/80">{label}</p>
          <p className="text-[11px] font-mono text-white/30">{desc}</p>
        </div>
        <span className="text-xs font-mono text-blue-400">{value}{unit}</span>
      </div>
      <input
        type="range" min={min} max={max} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full accent-blue-500 cursor-pointer h-1.5"
      />
    </div>
  );
}

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [cfg, setCfg] = useState({
    language: "English",
    provider: "Groq (Primary)",
    model: "llama3-8b-8192",
    voice: "Ritu (Sarvam Bulbul v3)",
    theme: "Sovereign Dark",
    pace: 1.1,
    temperature: 0.7,
    visionInterval: 30,
  });
  const set = (key: string) => (val: any) => setCfg(s => ({ ...s, [key]: val }));

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <InnerLayout>
      <div className="min-h-screen bg-black text-white px-8 py-10 overflow-y-auto custom-scrollbar">
      {/* Header */}
      <div className="mb-10 flex items-end justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-[0.3em] font-mono text-white/30">System Configuration</p>
          <h1 className="text-3xl font-semibold mt-1">Settings</h1>
          <p className="text-white/40 text-sm mt-1">Configure NIA's core behaviour and interface</p>
        </div>
        <motion.button
          onClick={handleSave}
          whileTap={{ scale: 0.95 }}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-colors duration-300 ${saved ? "bg-green-600 text-white" : "bg-blue-600 hover:bg-blue-500 text-white"}`}
        >
          {saved ? <Check size={14} /> : <Save size={14} />}
          {saved ? "Saved!" : "Save Changes"}
        </motion.button>
      </div>

      {/* Sovereign Identity */}
      <Section title="Sovereign Identity" icon={Shield}>
        <div className="flex items-center justify-between py-4 px-2">
            <div className="flex-1">
                <p className="text-sm text-white/80">Permanent Hash ID</p>
                <p className="text-[10px] font-mono text-purple-400 mt-1 opacity-80 break-all leading-relaxed">
                    {saved ? process.env.NEXT_PUBLIC_NIA_SOVEREIGN_ID || "2617656e...f66" : "••••••••••••••••••••••••••••••••"}
                </p>
            </div>
            <button 
                onClick={() => setSaved(!saved)} 
                className="text-[10px] font-mono text-white/20 hover:text-white/60 transition-colors uppercase tracking-widest border border-white/5 px-3 py-1 rounded-lg"
            >
                {saved ? "Hide" : "Reveal"}
            </button>
        </div>
        <div className="p-3 bg-purple-500/5 rounded-xl border border-purple-500/10 mt-2">
            <p className="text-[10px] text-purple-300 opacity-60 flex items-center gap-2">
                <Brain size={10} /> Identity is cryptographic and anchored to local logic DNA.
            </p>
        </div>
      </Section>

      {/* AI Brain */}
      <Section title="AI Brain" icon={BrainCircuit}>
        <SelectRow 
            label="Primary Intelligence Core" 
            desc="The default brain for all Hub interactions" 
            options={["NIA Sovereign (Local)", "Gemini Cloud", "Groq Fallback"]} 
            value={cfg.provider === "NIA Sovereign (Local)" ? "NIA Sovereign (Local)" : cfg.provider} 
            onChange={set("provider")} 
        />
        <SelectRow 
            label="Default Operation Mode" 
            desc="Starting logic state for new sessions" 
            options={["Fast Execution", "Strategic Planning"]} 
            value={cfg.model === "planning" ? "Strategic Planning" : "Fast Execution"} 
            onChange={(val: string) => set("model")(val === "Strategic Planning" ? "planning" : "execute")} 
        />
        <SliderRow label="Inference Creativity" desc="Controls logic temperature (0 = precise, 1 = creative)" min={0} max={1} value={cfg.temperature} onChange={set("temperature")} unit="" />
      </Section>

      {/* Voice */}
      <Section title="Voice & Speech" icon={Volume2}>
        <SelectRow label="Voice Model" desc="Sarvam AI Bulbul speaker" options={["Ritu (Sarvam Bulbul v3)", "Neha (Sarvam Bulbul v3)", "Priya (Sarvam Bulbul v3)"]} value={cfg.voice} onChange={set("voice")} />
        <SliderRow label="Speech Pace" desc="Speed of voice synthesis (1.0 = natural)" min={0.5} max={2} value={cfg.pace} onChange={set("pace")} unit="x" />
        <SelectRow label="Language" desc="Primary spoken language" options={["English", "Hindi", "Hinglish", "Tamil"]} value={cfg.language} onChange={set("language")} />
      </Section>

      {/* Vision */}
      <Section title="Vision Engine" icon={Eye}>
        <SliderRow label="Analysis Interval" desc="Seconds between screen captures when idle" min={10} max={120} value={cfg.visionInterval} onChange={set("visionInterval")} unit="s" />
        <SelectRow label="Vision Model" desc="Multimodal VLM for screen understanding" options={["Gemini 1.5 Flash", "Gemini 1.5 Pro"]} value="Gemini 1.5 Flash" onChange={() => {}} />
      </Section>

      {/* Appearance */}
      <Section title="Appearance" icon={Palette}>
        <SelectRow label="Theme" desc="UI color scheme" options={["Sovereign Dark", "Nebula Black", "Ghost White"]} value={cfg.theme} onChange={set("theme")} />
        <SelectRow label="Language" desc="Interface language" options={["English", "Hindi"]} value={cfg.language} onChange={set("language")} />
      </Section>
      </div>
    </InnerLayout>
  );
}
