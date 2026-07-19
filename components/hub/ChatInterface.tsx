"use client";

import { useRef, useEffect } from "react";
import { motion } from "framer-motion";

type Message = {
    id: string;
    role: "user" | "nia";
    content: string;
};

export default function ChatInterface({ messages }: { messages: Message[] }) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({
                top: scrollRef.current.scrollHeight,
                behavior: "smooth"
            });
        }
    }, [messages]);

    return (
        <div className="flex-1 w-full h-full min-h-0 flex flex-col pt-2">
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto custom-scrollbar px-4 space-y-4 pb-4"
            >
                {messages.length === 0 ? (
                    <div className="flex w-full h-full items-center justify-center text-white/30 text-xs font-mono tracking-widest uppercase">
                        Awaiting Command...
                    </div>
                ) : (
                    messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex flex-col w-full ${msg.role === "user" ? "items-end" : "items-start"
                                }`}
                        >
                            <div
                                className={`flex items-center gap-2 mb-1 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"
                                    }`}
                            >
                                <span className="text-[10px] uppercase tracking-widest font-mono text-white/50">
                                    {msg.role === "user" ? "You" : "NIA"}
                                </span>
                                {msg.role === "nia" && (
                                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
                                )}
                            </div>
                            <div
                                className={`px-3 py-2 rounded-xl text-xs leading-relaxed w-fit max-w-[95%] ${msg.role === "user"
                                    ? "bg-purple-600/20 border border-purple-500/30 text-white rounded-tr-none"
                                    : "bg-white/5 border border-white/10 text-white/80 rounded-tl-none backdrop-blur-md"
                                    }`}
                            >
                                {msg.content}
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
}
