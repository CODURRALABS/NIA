"use client";

import React, { useState, useEffect } from "react";
import InnerLayout from "@/components/layouts/InnerLayout";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Brain, 
  Search, 
  Trash2, 
  Clock, 
  Tag, 
  Filter, 
  BookOpen, 
  MoreVertical, 
  Edit3, 
  Download,
  Terminal
} from "lucide-react";

interface Conversation {
  id: string;
  title: string;
  summary: string;
  history: { role: string; content: string }[];
  tags: string[];
  timestamp: string;
  isUnlocked: boolean;
}

// Helper to generate random binary string
const generateBinary = (length: number) => {
  return Array.from({ length }, () => (Math.random() > 0.5 ? "1" : "0")).join("");
};

const BinaryText = ({ text, isUnlocked }: { text: string; isUnlocked: boolean }) => {
  const [display, setDisplay] = useState(generateBinary(text.length));

  useEffect(() => {
    if (isUnlocked) {
      setDisplay(text);
      return;
    }

    const interval = setInterval(() => {
      setDisplay(generateBinary(text.length));
    }, 100);

    return () => clearInterval(interval);
  }, [isUnlocked, text]);

  return <span className="font-mono break-all">{display}</span>;
};

export default function MemoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    // Load conversations from local storage
    const stored = localStorage.getItem("nia_sovereign_memories");
    if (stored) {
      try {
        setConversations(JSON.parse(stored));
      } catch (e) {
        setConversations([]);
      }
    }
  }, []);

  const saveToStorage = (updated: Conversation[]) => {
    setConversations(updated);
    localStorage.setItem("nia_sovereign_memories", JSON.stringify(updated));
  };

  const deleteConversation = (id: string) => {
    const updated = conversations.filter(c => c.id !== id);
    saveToStorage(updated);
    if (selectedId === id) setSelectedId(null);
  };

  const renameConversation = (id: string, newTitle: string) => {
    const updated = conversations.map(c => 
      c.id === id ? { ...c, title: newTitle } : c
    );
    saveToStorage(updated);
  };

  const filtered = conversations.filter(c => 
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.summary.toLowerCase().includes(search.toLowerCase())
  );

  const selected = conversations.find(c => c.id === selectedId);

  return (
    <InnerLayout>
      <div className="min-h-screen bg-black text-white flex flex-col overflow-hidden select-none">
        
        {/* Header */}
        <div className="px-8 pt-12 pb-8 border-b border-white/5 flex items-end justify-between bg-gradient-to-b from-neutral-900/20 to-transparent">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Terminal size={12} className="text-purple-500 animate-pulse" />
              <p className="text-[10px] uppercase tracking-[0.4em] font-mono text-white/40">Sovereign Logic Vault</p>
            </div>
            <h1 className="text-4xl font-bold tracking-tight">Memory Bank</h1>
            <p className="text-white/30 text-xs mt-2 font-mono uppercase tracking-widest">
                {conversations.length} Active Records // Encrypted Vector Space
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-white/5 border border-white/5 rounded-2xl px-4 py-2 hover:border-white/20 transition-all">
              <Search size={14} className="text-white/20" />
              <input 
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Query Binary Space..."
                className="bg-transparent text-xs text-white/80 outline-none placeholder:text-white/10 w-48 font-mono"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-1 min-h-0 overflow-hidden">
          
          {/* Conversation List */}
          <div className="w-[400px] border-r border-white/5 overflow-y-auto custom-scrollbar p-6 space-y-4">
            <AnimatePresence>
              {filtered.map((conv) => (
                <motion.div
                  key={conv.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  onClick={() => setSelectedId(conv.id)}
                  className={cn(
                    "group relative p-5 rounded-2xl border transition-all duration-300 cursor-pointer overflow-hidden",
                    selectedId === conv.id 
                      ? "bg-white/10 border-white/20 shadow-[0_10px_30px_rgba(168,85,247,0.1)]" 
                      : "bg-white/5 border-white/5 hover:bg-white/8 hover:translate-x-1"
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] font-mono text-white/20 flex items-center gap-2">
                        <Clock size={10} /> {new Date(conv.timestamp).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          const newName = prompt("Rename Conversation:", conv.title);
                          if (newName) renameConversation(conv.id, newName);
                        }}
                        className="p-1.5 hover:bg-white/10 rounded-lg text-white/40 hover:text-white"
                      >
                        <Edit3 size={12} />
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm("Permanently delete this memory thread?")) deleteConversation(conv.id);
                        }}
                        className="p-1.5 hover:bg-red-500/20 rounded-lg text-white/40 hover:text-red-400"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                  
                  <h3 className="text-sm font-semibold text-white/80 mb-2 truncate">
                    {conv.title}
                  </h3>
                  
                  <div className="text-[10px] text-purple-400/60 leading-relaxed overflow-hidden">
                    <BinaryText text={conv.summary.slice(0, 100)} isUnlocked={selectedId === conv.id} />
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {filtered.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-white/10 space-y-4 opacity-50">
                <Brain size={48} strokeWidth={1} />
                <p className="font-mono text-xs uppercase tracking-widest text-center">Memory space is offline.<br/>Initiate Hub chat to anchor logic.</p>
              </div>
            )}
          </div>

          {/* Reasoning Detail View */}
          <div className="flex-1 bg-[#050505] overflow-y-auto custom-scrollbar p-12">
            <AnimatePresence mode="wait">
              {selected ? (
                <motion.div
                  key={selected.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="max-w-3xl mx-auto space-y-12"
                >
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="h-0.5 w-12 bg-purple-500/50" />
                      <span className="text-[10px] font-mono text-purple-400 uppercase tracking-[0.5em]">Cognitive Decode</span>
                    </div>
                    <h2 className="text-4xl font-bold text-white/90 leading-tight">
                        {selected.title}
                    </h2>
                  </div>

                  <div className="space-y-8">
                    {selected.history.map((msg, i) => (
                      <div key={i} className={cn(
                        "p-6 rounded-2xl border transition-all",
                        msg.role === "user" 
                          ? "bg-white/5 border-white/5 ml-12" 
                          : "bg-purple-500/5 border-purple-500/10 mr-12 shadow-[0_0_40px_rgba(168,85,247,0.02)]"
                      )}>
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-[9px] font-mono uppercase tracking-widest opacity-30">
                                {msg.role === "user" ? "USER_PROMPT" : "NIA_SOVEREIGN"}
                            </span>
                        </div>
                        <p className="text-sm text-white/70 leading-relaxed whitespace-pre-wrap">
                            {msg.content}
                        </p>
                      </div>
                    ))}
                  </div>
                  
                  <div className="pt-12 border-t border-white/5 flex items-center justify-between">
                    <div className="flex gap-2">
                      {selected.tags.map(tag => (
                        <span key={tag} className="px-3 py-1 bg-white/5 border border-white/5 rounded-full text-[10px] font-mono text-white/30 truncate">
                          #{tag}
                        </span>
                      ))}
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl text-[10px] font-mono text-white/40 border border-white/5 transition-all">
                      <Download size={14} /> EXPORT_BINARY
                    </button>
                  </div>
                </motion.div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-white/5 space-y-4">
                  <BookOpen size={64} strokeWidth={1} />
                  <p className="font-mono text-sm uppercase tracking-[0.2em]">Select a logic chain to decode</p>
                </div>
              )}
            </AnimatePresence>
          </div>

        </div>
      </div>
    </InnerLayout>
  );
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ");
}
