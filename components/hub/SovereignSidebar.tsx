"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ChevronLeft,
    ChevronRight,
    Settings,
    LayoutDashboard,
    MessageSquare,
    History,
    Shield,
    LogOut,
    User
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SovereignSidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const router = useRouter();

    const navItems = [
        { icon: LayoutDashboard, label: "Dashboard", href: "/hub" },
        { icon: MessageSquare, label: "Agent", href: "/agent" },
        { icon: History, label: "Task History", href: "#" },
        { icon: Shield, label: "Sovereign Core", href: "#" },
    ];

    return (
        <motion.div
            animate={{ width: isOpen ? 260 : 80 }}
            onMouseEnter={() => setIsOpen(true)}
            onMouseLeave={() => setIsOpen(false)}
            className="group relative h-full bg-[#050505]/40 backdrop-blur-2xl border-r border-white/10 flex flex-col transition-all duration-300 z-50"
        >
            {/* Header / Logo Section */}
            <div className="p-6 flex items-center justify-center border-b border-white/5">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <span className="font-bold text-white text-xs">N</span>
                </div>
                {isOpen && (
                    <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="ml-3 font-mono text-sm tracking-widest text-white/80"
                    >
                        SOVEREIGN
                    </motion.span>
                )}
            </div>

            {/* Nav Links */}
            <nav className="flex-1 px-4 py-8 space-y-2">
                {navItems.map((item, idx) => (
                    <Link
                        key={idx}
                        href={item.href}
                        className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-all text-white/40 hover:text-white group/item"
                    >
                        <item.icon size={20} className="shrink-0" />
                        {isOpen && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="text-xs font-mono tracking-wider uppercase"
                            >
                                {item.label}
                            </motion.span>
                        )}
                    </Link>
                ))}
            </nav>

            {/* Footer: User & Settings */}
            <div className="p-4 border-t border-white/5 space-y-2">

                {/* User Profile / Login Option */}
                <button
                    className="w-full flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-all text-white/40 hover:text-white group/profile"
                >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500/30 to-blue-500/30 border border-white/10 flex items-center justify-center shrink-0">
                        <User size={16} />
                    </div>
                    {isOpen && (
                        <div className="flex-1 text-left min-w-0">
                            <p className="text-[10px] font-bold text-white/80 truncate">Sovereign Admin</p>
                            <p className="text-[8px] font-mono text-white/30 truncate uppercase">Premium Access</p>
                        </div>
                    )}
                </button>

                {/* Settings Button (Personalization) */}
                <button
                    onClick={() => router.push("/personalization")}
                    className="w-full flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-all text-white/40 hover:text-white"
                >
                    <Settings size={20} className="shrink-0" />
                    {isOpen && (
                        <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xs font-mono tracking-wider uppercase"
                        >
                            Personalize
                        </motion.span>
                    )}
                </button>

                {/* Log Out (Optional Mock) */}
                {isOpen && (
                    <button className="w-full mt-4 flex items-center gap-4 p-3 rounded-xl text-red-400/50 hover:text-red-400 hover:bg-red-400/5 transition-all">
                        <LogOut size={16} />
                        <span className="text-[10px] uppercase font-mono tracking-widest">Disconnect</span>
                    </button>
                )}
            </div>
        </motion.div>
    );
}
