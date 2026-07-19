"use client";

import React, { useState } from "react";
import { BrainCircuit, ChevronUp, Play, Zap, Settings, Shield, Cpu } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import "./AIInput.css";

interface AIInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
  variant?: "full" | "compact";
  model: "nia" | "gemini";
  setModel: (model: "nia" | "gemini") => void;
  mode: "execute" | "planning";
  setMode: (mode: "execute" | "planning") => void;
}

export default function AIInput({ 
  value, 
  onChange, 
  onSubmit, 
  loading, 
  variant = "full",
  model,
  setModel,
  mode,
  setMode
}: AIInputProps) {
  const [isAppendixOpen, setIsAppendixOpen] = useState(false);
  const [vocalMode, setVocalMode] = useState<"manual" | "listening">("manual");
  const [isModelMenuOpen, setIsModelMenuOpen] = useState(false);
  const [isModeMenuOpen, setIsModeMenuOpen] = useState(false);
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  const suggestions = [
    "Create an image",
    "Give me ideas",
    "Write a text",
    "Create a chart",
    "Plan a trip",
    "Help me pick",
    "Write a Python script"
  ];

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
  };

  return (
    <div className={cn("AI-Input-Wrapper", variant === "compact" && "compact-mode")}>
      <div className={cn("AI-Input", variant === "compact" && "slick-panel")}>
        <input type="file" id="camera" accept="image/*" capture="environment" className="hidden" />
        <input type="file" id="photos" accept="image/*" className="hidden" />
        <input type="file" id="files" className="hidden" />
        <input id="mic-input" type="checkbox" className="hidden" />
        
        {variant === "full" && (
          <div className="chat-marquee">
            <ul>
              {suggestions.map((s, i) => (
                <li key={`s1-${i}`} onClick={() => handleSuggestionClick(s)}>{s}</li>
              ))}
            </ul>
            <ul>
              {suggestions.map((s, i) => (
                <li key={`s2-${i}`} onClick={() => handleSuggestionClick(s)}>{s}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Reasoning Status Indicator */}
        <AnimatePresence>
          {loading && (
            <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="reasoning-indicator"
            >
                <div className="reasoning-dots">
                    <span></span><span></span><span></span>
                </div>
                <span className="reasoning-text font-mono uppercase tracking-[0.3em]">Reasoning Pattern Detected...</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="chat-container">
          <div className="chat-wrapper" onClick={(e) => e.stopPropagation()}>
            <textarea 
              id="chat-input" 
              placeholder={loading ? "" : "Ask anything"}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              rows={1}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = target.scrollHeight + 'px';
              }}
            ></textarea>
            
            <div className="button-bar">
              <div className="left-buttons">
                <button 
                  type="button"
                  className="icon-btn attachment-btn"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log("[UI]: Attachment toggle triggered");
                    setIsAppendixOpen(!isAppendixOpen);
                  }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M4.5 3a2.5 2.5 0 0 1 5 0v9a1.5 1.5 0 0 1-3 0V5a.5.5 0 0 1 1 0v7a.5.5 0 0 0 1 0V3a1.5 1.5 0 1 0-3 0v9a2.5 2.5 0 0 0 5 0V5a.5.5 0 0 1 1 0v7a3.5 3.5 0 1 1-7 0z"></path>
                  </svg>
                </button>
                
                {/* Appendix Overlay */}
                <AnimatePresence>
                  {isAppendixOpen && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="appendix-overlay"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsAppendixOpen(false);
                        }}
                    >
                      <motion.div 
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        className="appendix-content" 
                        onClick={(e) => e.stopPropagation()}
                      >
                        <label htmlFor="camera">
                          <svg viewBox="0 0 16 16" fill="currentColor" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M10.5 8.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"></path>
                            <path d="M2 4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-1.172a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 9.172 2H6.828a2 2 0 0 0-1.414.586l-.828.828A2 2 0 0 1 3.172 4zm.5 2a.5.5 0 1 1 0-1 .5.5 0 0 1 0 1m9 2.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0"></path>
                          </svg>
                        </label>
                        <label htmlFor="photos">
                          <svg viewBox="0 0 16 16" fill="currentColor" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4.502 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3"></path>
                            <path d="M14.002 13a2 2 0 0 1-2 2h-10a2 2 0 0 1-2-2V5A2 2 0 0 1 2.002 3h10a2 2 0 0 1 2 2v8a2 2 0 0 1-1.998 2M14 11l-3.333-4.444a.5.5 0 0 0-.756-.048L7.13 10.37 5.4 8.785a.5.5 0 0 0-.69.014L2 12h12z"></path>
                          </svg>
                        </label>
                        <label htmlFor="files">
                          <svg viewBox="0 0 16 16" fill="currentColor" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                              <path d="M4.5 3a2.5 2.5 0 0 1 5 0v9a1.5 1.5 0 0 1-3 0V5a.5.5 0 0 1 1 0v7a.5.5 0 0 0 1 0V3a1.5 1.5 0 1 0-3 0v9a2.5 2.5 0 0 0 5 0V5a.5.5 0 0 1 1 0v7a3.5 3.5 0 1 1-7 0z"></path>
                          </svg>
                        </label>
                      </motion.div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <button 
                  type="button" 
                  className="icon-btn search-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    console.log("[UI]: Search triggered");
                  }}
                >
                  <svg viewBox="0 0 16 16" fill="currentColor" height="18" width="18" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"></path>
                  </svg>
                </button>
              </div>

              <div className="right-buttons">
                {/* Model Selector */}
                <div className="selector-group">
                  <button 
                    className={cn("dropdown-trigger", model === "nia" ? "nia-active" : "gemini-active")}
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsModelMenuOpen(!isModelMenuOpen);
                    }}
                  >
                    <span>{model === "nia" ? "NIA Engine" : "Gemini Core"}</span>
                    <ChevronUp className={cn("w-3 h-3 transition-transform", isModelMenuOpen && "rotate-180")} />
                  </button>
                  {isModelMenuOpen && (
                    <div className="dropdown-list" onClick={(e) => e.stopPropagation()}>
                      <div className="list-item" onClick={() => { setModel("nia"); setIsModelMenuOpen(false); }}>
                        <BrainCircuit className="w-3 h-3 mr-2" /> NIA Sovereign
                      </div>
                      <div className="list-item" onClick={() => { setModel("gemini"); setIsModelMenuOpen(false); }}>
                        <Zap className="w-3 h-3 mr-2" /> Gemini Cloud
                      </div>
                    </div>
                  )}
                </div>

                {/* Mode Selector */}
                <div className="selector-group">
                  <button 
                    className={cn("dropdown-trigger", mode === "planning" ? "plan-active" : "fast-active")}
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsModeMenuOpen(!isModeMenuOpen);
                    }}
                  >
                    <span>{mode === "planning" ? "Planning" : "Execute"}</span>
                    <ChevronUp className={cn("w-3 h-3 transition-transform", isModeMenuOpen && "rotate-180")} />
                  </button>
                  {isModeMenuOpen && (
                    <div className="dropdown-list" onClick={(e) => e.stopPropagation()}>
                      <div className="list-item" onClick={() => { setMode("planning"); setIsModeMenuOpen(false); }}>
                        <Settings className="w-3 h-3 mr-2" /> Strategic Planning
                      </div>
                      <div className="list-item" onClick={() => { setMode("execute"); setIsModeMenuOpen(false); }}>
                        <Zap className="w-3 h-3 mr-2" /> Fast Execution
                      </div>
                    </div>
                  )}
                </div>

                <button 
                  type="button"
                  className={cn("icon-btn mic-btn", vocalMode === "listening" && "vocal-active")} 
                  onClick={(e) => {
                    e.stopPropagation();
                    setVocalMode(vocalMode === "manual" ? "listening" : "manual");
                  }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5"></path>
                    <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3"></path>
                  </svg>
                  {vocalMode === "listening" && (
                    <motion.div 
                      layoutId="listening-glow"
                      className="absolute inset-0 bg-blue-500/20 rounded-full blur-md animate-pulse"
                    />
                  )}
                </button>
                
                <button 
                  className="send-trigger" 
                  onClick={(e) => {
                    e.stopPropagation();
                    onSubmit();
                  }}
                  disabled={loading || !value.trim()}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
