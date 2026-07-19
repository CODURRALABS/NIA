"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Terminal, Sparkles, BrainCircuit, X } from "lucide-react";

export default function ProactiveHub() {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [thoughts, setThoughts] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [thoughts, response]);

  const handleExecute = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setResponse("");
    setThoughts(prev => [...prev, `> ${prompt}`]);
    
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, mode: "execute" })
      });
      const data = await res.json();
      
      if (data.response) {
        setResponse(data.response);
        setThoughts(prev => [...prev, `NIA: ${data.response}`]);
      } else {
        setThoughts(prev => [...prev, `ERR: ${data.error || "Unknown bridge failure"}`]);
      }
    } catch (err) {
      setThoughts(prev => [...prev, `ERR: Connection to Pulse Hub failed.`]);
    } finally {
      setLoading(false);
      setPrompt("");
    }
  };

  return (
    <>
      {/* Floating Trigger */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-10 right-10 w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-[0_0_40px_rgba(37,99,235,0.4)] z-50 border border-white/20"
      >
        <Sparkles className="text-white" size={24} />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed bottom-28 right-10 w-[400px] h-[500px] bg-neutral-900/90 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-5 border-b border-white/5 flex items-center justify-between bg-white/5">
              <div className="flex items-center gap-2">
                <BrainCircuit size={18} className="text-blue-400" />
                <span className="text-sm font-semibold tracking-wide">Proactive Hub</span>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-white/30 hover:text-white transition-colors">
                <X size={18} />
              </button>
            </div>

            {/* Terminal Feed */}
            <div ref={scrollRef} className="flex-1 p-5 overflow-y-auto font-mono text-xs space-y-3 custom-scrollbar">
              <div className="text-white/20 italic mb-4">NIA Sovereign Terminal v12.4 initialized...</div>
              {thoughts.map((t, i) => (
                <div key={i} className={t.startsWith(">") ? "text-blue-400" : t.startsWith("ERR") ? "text-red-400" : "text-white/80"}>
                  {t}
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-blue-400/50">
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                  >
                    <Terminal size={12} />
                  </motion.div>
                  <span>Processing logic DNA...</span>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 bg-black/40 border-t border-white/5">
              <div className="relative">
                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleExecute()}
                  placeholder="Issue a command..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white outline-none focus:border-blue-500/50 transition-colors"
                />
                <button
                  onClick={handleExecute}
                  className="absolute right-2 top-1.5 p-2 text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
