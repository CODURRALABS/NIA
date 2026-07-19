"use client";

import { motion } from "framer-motion";
import { Check, Zap, ShieldCheck, Brain, Crown, Star } from "lucide-react";

const features = [
    { icon: Brain, label: "Unlimited Sovereign Tasks", desc: "No daily limits. NIA works for you 24/7." },
    { icon: ShieldCheck, label: "Encrypted Cloud Backup", desc: "AES-256 client-side encrypted memory sync." },
    { icon: Zap, label: "Vibe Coding Priority", desc: "Access to NIA's self-evolution engine." },
    { icon: Crown, label: "Admin Sovereignty Mode", desc: "Full system-level access across all devices." },
    { icon: Star, label: "Priority Vocal Presence", desc: "Upgraded StyleTTS2 voice — emotionally aware." },
    { icon: Check, label: "Early Access Features", desc: "Beta Pixels-to-Actions and multi-device sync." },
];

const plans = [
    {
        name: "Trial",
        price: "Free",
        priceNote: "14 Days",
        color: "border-white/20",
        cta: "Start Free Trial",
        ctaStyle: "bg-white/10 hover:bg-white/20 text-white",
        features: ["Core NIA assistance", "Local processing only", "Basic voice commands"],
    },
    {
        name: "Empire",
        price: "₹499",
        priceNote: "/ month",
        color: "border-blue-500",
        cta: "UPI Quick-Pay (Monthly)",
        ctaStyle: "bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_24px_rgba(59,130,246,0.4)]",
        popular: true,
        features: ["Unlimited tasks", "Cloud backup (encrypted)", "Vibe Coding engine", "Admin Sovereignty Mode"],
    },
    {
        name: "Sovereign",
        price: "₹4,999",
        priceNote: "/ yearly",
        color: "border-purple-500",
        cta: "UPI Quick-Pay (Yearly)",
        ctaStyle: "bg-purple-600/80 hover:bg-purple-500 text-white",
        features: ["Everything in Empire", "Priority Voice", "Early access betas", "2 months free"],
    },
];

export default function EmpireTierPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white overflow-hidden">

            {/* Hero */}
            <div className="relative text-center pt-24 pb-16 px-6">
                <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 to-transparent pointer-events-none" />
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full text-sm text-blue-300 font-mono tracking-widest mb-6">
                        <Crown size={14} /> EMPIRE TIER — 2026
                    </div>
                    <h1 className="text-5xl md:text-7xl font-extralight tracking-tight mb-4">
                        Sovereign <span className="text-blue-400">Intelligence.</span>
                    </h1>
                    <p className="text-white/40 text-lg max-w-xl mx-auto font-light">
                        Unlock the full power of NIA. For Indian students and SMBs who need a true AI employee — not just a chatbot.
                    </p>
                </motion.div>
            </div>

            {/* Feature Grid */}
            <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-20">
                {features.map((f, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * i, duration: 0.5 }}
                        className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-start gap-4 hover:border-white/20 transition-colors"
                    >
                        <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 shrink-0">
                            <f.icon size={18} />
                        </div>
                        <div>
                            <p className="font-semibold text-white/90 text-sm">{f.label}</p>
                            <p className="text-white/40 text-xs mt-1">{f.desc}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Pricing Cards */}
            <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-6 mb-24">
                {plans.map((plan, i) => (
                    <motion.div
                        key={plan.name}
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 * i, duration: 0.6 }}
                        className={`relative rounded-2xl bg-white/5 border ${plan.color} p-7 flex flex-col backdrop-blur-md`}
                    >
                        {plan.popular && (
                            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-mono px-4 py-1 rounded-full tracking-wider">
                                MOST POPULAR
                            </div>
                        )}
                        <p className="text-white/50 text-xs font-mono tracking-widest uppercase mb-2">{plan.name}</p>
                        <div className="flex items-baseline gap-1 mb-1">
                            <span className="text-4xl font-light text-white">{plan.price}</span>
                            <span className="text-white/30 text-sm">{plan.priceNote}</span>
                        </div>
                        <ul className="flex flex-col gap-2 mt-6 mb-8 flex-1">
                            {plan.features.map((feat) => (
                                <li key={feat} className="flex items-center gap-2 text-sm text-white/70">
                                    <Check size={13} className="text-blue-400 shrink-0" />
                                    {feat}
                                </li>
                            ))}
                        </ul>
                        <button className={`w-full py-2.5 rounded-xl text-sm font-mono tracking-wider transition-all duration-300 ${plan.ctaStyle}`}>
                            {plan.cta}
                        </button>
                    </motion.div>
                ))}
            </div>

            {/* Payment info */}
            <div className="text-center pb-16 px-6">
                <p className="text-white/30 text-sm font-mono tracking-wider">
                    🇮🇳 UPI / Razorpay / PayU — Instant activation after payment. Cancel anytime.
                </p>
                <p className="text-white/20 text-xs mt-2">
                    GST included. Pricing in INR. Special pricing for verified students available on request.
                </p>
            </div>
        </div>
    );
}
