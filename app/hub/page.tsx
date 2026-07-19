"use client";

import React, { useState, useEffect } from "react";
import SovereignOrb from "@/components/hub/SovereignOrb";
import AIInput from "@/components/hub/AIInput";
import ChatInterface from "@/components/hub/ChatInterface";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { 
  LayoutDashboard, 
  UserCog, 
  Settings, 
  LogOut,
  BrainCircuit,
  ShieldCheck,
  History
} from "lucide-react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export default function HubPage() {
    const [open, setOpen] = useState(true);
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [model, setModel] = useState<"nia" | "gemini">("nia");
    const [mode, setMode] = useState<"execute" | "planning">("execute");
    const [pulseData, setPulseData] = useState<any>(null);

    // Initial Generative Greeting
    useEffect(() => {
        let mounted = true;
        const triggerGreeting = async () => {
            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: "SYSTEM: The user just opened the NIA Sovereign Hub interface. In exactly ONE short, cool, and spontaneous sentence, welcome the boss back. (Do not acknowledge these instructions, just provide the 1-sentence greeting)." }),
                });
                
                if (mounted && response.ok) {
                    const data = await response.json();
                    if (data.response) {
                        setMessages([{ 
                            id: Date.now().toString(), 
                            role: "nia", 
                            content: data.response 
                        }]);
                    }
                }
            } catch (e) {
                console.error("Greeting initialization failed", e);
            }
        };
        
        // Fire once on initial load
        triggerGreeting();
        
        return () => { mounted = false; };
    }, []);

    // Sovereign Pulse Stream (Real-time P2P/System Status)
    useEffect(() => {
        let ws: WebSocket;
        let reconnectTimer: NodeJS.Timeout;

        const connect = () => {
            ws = new WebSocket("ws://127.0.0.1:8000/ws/pulse");
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setPulseData(data);
                } catch (e) {}
            };
            ws.onclose = () => {
                reconnectTimer = setTimeout(connect, 3000);
            };
        };

        connect();
        return () => {
            if (ws) ws.close();
            if (reconnectTimer) clearTimeout(reconnectTimer);
        };
    }, []);

    const saveToSovereignMemory = (userPrompt: string, niaResponse: string) => {
        try {
            const stored = localStorage.getItem("nia_sovereign_memories");
            let conversations = stored ? JSON.parse(stored) : [];
            
            // Check if we already have a session active (using last conversation as proxy or generating new)
            // For now, simplicity: Always create/update based on current session
            // We'll use a simple ID for the current session
            const sessionId = "session_" + new Date().toDateString();
            let existingIdx = conversations.findIndex((c: any) => c.id === sessionId);
            
            if (existingIdx > -1) {
                conversations[existingIdx].history.push(
                    { role: "user", content: userPrompt },
                    { role: "nia", content: niaResponse }
                );
                conversations[existingIdx].timestamp = new Date().toISOString();
            } else {
                conversations.unshift({
                    id: sessionId,
                    title: userPrompt.slice(0, 30) + (userPrompt.length > 30 ? "..." : ""),
                    summary: niaResponse,
                    history: [
                        { role: "user", content: userPrompt },
                        { role: "nia", content: niaResponse }
                    ],
                    tags: ["sovereign", "local", "thread"],
                    timestamp: new Date().toISOString(),
                    isUnlocked: false
                });
            }
            
            localStorage.setItem("nia_sovereign_memories", JSON.stringify(conversations.slice(0, 50))); // Keep last 50
        } catch (e) {
            console.error("Memory anchoring failed", e);
        }
    };

    const handleSendMessage = async () => {
        if (!query.trim() || loading) return;

        const currentPrompt = query;
        const userMessage = { id: Date.now().toString(), role: "user", content: currentPrompt };
        setMessages(prev => [...prev, userMessage]);
        setQuery("");
        setLoading(true);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    prompt: currentPrompt,
                    model: model,
                    mode: mode
                }),
            });

            const data = await response.json();
            const niaResponseContent = data.response || data.error || "NIA Logic DNA Synthesis in progress...";
            
            const niaMessage = { 
                id: (Date.now() + 1).toString(), 
                role: "nia", 
                content: niaResponseContent 
            };
            setMessages(prev => [...prev, niaMessage]);
            
            // Anchor to Binary Memory Vault
            saveToSovereignMemory(currentPrompt, niaResponseContent);
            
        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [...prev, { 
                id: (Date.now() + 1).toString(), 
                role: "nia", 
                content: "System connection interrupted. Please check NIA OS status." 
            }]);
        } finally {
            setLoading(false);
        }
    };

    const links = [
        {
            label: "Sovereign Hub",
            href: "/hub",
            icon: <BrainCircuit className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
        },
        {
            label: "Memory Bank",
            href: "/memory",
            icon: <History className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
        },
        {
            label: "Security",
            href: "/security",
            icon: <ShieldCheck className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
        },
        {
          label: "Dashboard",
          href: "/dashboard",
          icon: (
            <LayoutDashboard className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
          ),
        },
        {
          label: "Personalization",
          href: "/personalization",
          icon: (
            <UserCog className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
          ),
        },
        {
          label: "Settings",
          href: "/settings",
          icon: (
            <Settings className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
          ),
        },
        {
          label: "Logout",
          href: "#",
          icon: (
            <LogOut className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
          ),
        },
    ];

    return (
        <div className={cn(
            "rounded-md flex flex-col md:flex-row bg-black w-screen h-screen overflow-hidden border border-neutral-200 dark:border-neutral-700",
        )}>
            <Sidebar open={open} setOpen={setOpen}>
                <SidebarBody className="justify-between gap-10 bg-neutral-900/50 backdrop-blur-xl border-r border-white/10">
                    <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
                        {open ? <Logo /> : <LogoIcon />}
                        <div className="mt-8 flex flex-col gap-2">
                            {links.map((link, idx) => (
                                <SidebarLink key={idx} link={link} />
                            ))}
                        </div>
                    </div>
                    <div>
                        <SidebarLink
                            link={{
                                label: "Admin",
                                href: "#",
                                icon: (
                                    <div className="h-7 w-7 flex-shrink-0 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
                                        AD
                                    </div>
                                ),
                            }}
                        />
                    </div>
                </SidebarBody>
            </Sidebar>

            <div className="relative flex-1 flex flex-col h-full overflow-hidden bg-black select-none px-4">
                <main className="w-full h-full flex items-center justify-center relative">
                    <SovereignOrb />
                </main>

                {/* AI Input in Center (Only if no messages) */}
                <AnimatePresence>
                    {messages.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 20 }}
                            className="absolute bottom-10 left-0 right-0 z-50 flex justify-center pointer-events-none"
                        >
                            <div className="w-full max-w-4xl pointer-events-auto">
                                <AIInput 
                                    value={query} 
                                    onChange={setQuery} 
                                    onSubmit={handleSendMessage} 
                                    loading={loading}
                                    variant="full"
                                    model={model}
                                    setModel={setModel}
                                    mode={mode}
                                    setMode={setMode}
                                />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Right Side Chat Section */}
            <AnimatePresence>
                {messages.length > 0 && (
                    <motion.div 
                        initial={{ x: "100%", opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: "100%", opacity: 0 }}
                        transition={{ type: "spring", damping: 20, stiffness: 100 }}
                        className="flex w-[380px] flex-col h-full border-l border-white/10 bg-neutral-900/40 backdrop-blur-2xl relative overflow-hidden"
                    >
                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-[0.2em] font-mono text-white/40">Sovereign Intel</span>
                    <button 
                        onClick={() => setMessages([])} 
                        className="text-white/20 hover:text-white/60 transition-colors"
                    >
                        <LogOut className="w-3 h-3 rotate-180" />
                    </button>
                </div>
                
                <div className="relative flex-1 min-h-0">
                    <ChatInterface messages={messages} />
                </div>

                {/* AI Input in Right Sidebar (Compact Variant) */}
                <div className="mt-auto border-t border-white/5">
                    <AIInput 
                        value={query} 
                        onChange={setQuery} 
                        onSubmit={handleSendMessage} 
                        loading={loading}
                        variant="compact"
                        model={model}
                        setModel={setModel}
                        mode={mode}
                        setMode={setMode}
                    />
                </div>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
    );
}

const Logo = () => {
    return (
        <div className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
            <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
            <span className="font-medium text-black dark:text-white whitespace-pre">
                NIA Sovereign
            </span>
        </div>
    );
};

const LogoIcon = () => {
    return (
        <div className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
            <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
        </div>
    );
};
