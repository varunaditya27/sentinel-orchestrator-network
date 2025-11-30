"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import { ScrambleText } from "@/components/ScrambleText";
import { HolographicCard } from "@/components/HolographicCard";
import { Shield, Zap, Globe, Activity, Terminal, Cpu, Lock, Server, Database } from "lucide-react";
import Image from "next/image";

// --- Utility Components ---

const TechCorner = ({ className }: { className?: string }) => (
    <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M1 1V6M1 1H6" stroke="currentColor" strokeWidth="2" />
    </svg>
);

const GlowingOrb = ({ color = "bg-neon-orchid" }: { color?: string }) => (
    <div className={`absolute w-[500px] h-[500px] ${color} rounded-full blur-[120px] opacity-20 pointer-events-none mix-blend-screen`} />
);

// --- Components ---

const GlowingOrb = ({ color = "cyan", size = "md" }) => {
    const sizeClasses = {
        sm: "w-32 h-32",
        md: "w-64 h-64",
        lg: "w-96 h-96",
    };

    const colorClasses = {
        cyan: "bg-cyan-500 shadow-cyan-500/50",
        purple: "bg-purple-500 shadow-purple-500/50",
        emerald: "bg-emerald-500 shadow-emerald-500/50",
        orange: "bg-orange-500 shadow-orange-500/50",
    };

    return (
        <div className={`absolute rounded-full blur-[100px] opacity-20 animate-pulse ${sizeClasses[size]} ${colorClasses[color]}`} />
    );
};

const AgentCard = ({ name, role, description, image, stats, color = "cyan", icon: Icon }) => {
    return (
        <motion.div
            whileHover={{ scale: 1.02, y: -5 }}
            className={`relative group overflow-hidden rounded-2xl border border-${color}-500/30 bg-black/40 backdrop-blur-md p-6 hover:border-${color}-400/60 transition-all duration-500`}
        >
            <div className={`absolute inset-0 bg-gradient-to-br from-${color}-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

            <div className="relative z-10 flex flex-col h-full">
                <div className="flex items-center justify-between mb-4">
                    <div className={`p-2 rounded-lg bg-${color}-500/20 text-${color}-400`}>
                        <Icon size={24} />
                    </div>
                    <div className="px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs font-mono text-white/70">
                        {role}
                    </div>
                </div>

                <h3 className="text-2xl font-bold text-white mb-2 font-mono tracking-tight">{name}</h3>
                <p className="text-gray-400 text-sm mb-6 flex-grow">{description}</p>

                {image && (
                    <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden border border-white/10 group-hover:border-white/20 transition-colors">
                        <Image
                            src={image}
                            alt={name}
                            fill
                            className="object-cover transition-transform duration-700 group-hover:scale-110"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                    </div>
                )}

                <div className="grid grid-cols-2 gap-2 mt-auto">
                    {stats.map((stat, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-2 border border-white/5">
                            <div className="text-xs text-gray-500 uppercase tracking-wider">{stat.label}</div>
                            <div className={`text-sm font-mono text-${color}-400`}>{stat.value}</div>
                        </div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

const SpecialistCard = ({ name, role, icon: Icon, color, description, features }) => (
    <motion.div
        whileHover={{ scale: 1.05 }}
        className={`p-4 rounded-xl border border-${color}-500/20 bg-black/60 backdrop-blur-sm hover:bg-${color}-900/10 hover:border-${color}-500/50 transition-all duration-300`}
    >
        <div className={`w-10 h-10 rounded-lg bg-${color}-500/20 flex items-center justify-center mb-3 text-${color}-400`}>
            <Icon size={20} />
        </div>
        <h4 className="text-lg font-bold text-white font-mono mb-1">{name}</h4>
        <div className={`text-xs text-${color}-400 mb-2 uppercase tracking-wider`}>{role}</div>
        <p className="text-gray-400 text-xs mb-3 leading-relaxed">{description}</p>
        <ul className="space-y-1">
            {features.map((feature, i) => (
                <li key={i} className="flex items-center text-xs text-gray-500">
                    <div className={`w-1 h-1 rounded-full bg-${color}-500 mr-2`} />
                    {feature}
                </li>
            ))}
        </ul>
    </motion.div>
);

const LiveTerminal = () => {
    const [logs, setLogs] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const logTemplates = [
        { msg: "[SENTINEL] Validating policy ID 8f9a...2b1c", color: "text-cyan-400" },
        { msg: "[ORACLE] Connecting to BlockScanner specialist...", color: "text-purple-400" },
        { msg: "[BLOCK_SCANNER] Verifying block height 9823412...", color: "text-orange-400" },
        { msg: "[MEMPOOL] Scanning for front-running patterns...", color: "text-blue-400" },
        { msg: "[REPLAY] Checking UTxO consumption history...", color: "text-red-400" },
        { msg: "[STAKE] Analyzing pool saturation: 42.5% (SAFE)", color: "text-emerald-400" },
        { msg: "[GOVERNANCE] Fetching proposal CIP-1694 metadata...", color: "text-yellow-400" },
        { msg: "[POLICY] Checking treasury cap compliance...", color: "text-pink-400" },
        { msg: "[SENTIMENT] Analyzing on-chain voting patterns...", color: "text-indigo-400" },
        { msg: "[TREASURY] Z-Score analysis: 0.42 (NORMAL)", color: "text-green-400" },
        { msg: "[MESSAGE_BUS] Broadcast: HIRE_REQUEST sig:a7b2...", color: "text-gray-500" },
        { msg: "[ORACLE] Consensus verified. Verdict: SAFE", color: "text-green-500 font-bold" },
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            const newLog = logTemplates[Math.floor(Math.random() * logTemplates.length)];
            const timestamp = new Date().toISOString().split("T")[1].split(".")[0];
            setLogs(prev => [...prev.slice(-8), `[${timestamp}] ${newLog.msg}`]);
        }, 1500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="font-mono text-xs bg-black/80 border border-white/10 rounded-lg p-4 h-64 overflow-hidden relative">
            <div className="absolute top-2 right-2 flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                <div className="w-2 h-2 rounded-full bg-green-500" />
            </div>
            <div className="text-gray-500 mb-2 border-b border-white/5 pb-2">system_status --monitor --verbose</div>
            <div className="space-y-1">
                <AnimatePresence>
                    {logs.map((log, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="truncate"
                        >
                            <span className="text-gray-600 mr-2">{log.split("] ")[0]}]</span>
                            <span className={log.includes("SAFE") ? "text-green-400" : "text-gray-300"}>
                                {log.split("] ").slice(1).join("] ")}
                            </span>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black to-transparent" />
        </div>
    );
};

export default function AboutPage() {
                                </div >
                            </div >
                        </motion.div >

        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative"
        >
            <div className="absolute -inset-10 bg-electric-cyan/20 blur-[100px] rounded-full" />
            <LiveTerminal />

            {/* Decorative lines */}
            <div className="absolute -right-12 top-1/2 w-24 h-[1px] bg-gradient-to-r from-white/20 to-transparent" />
            <div className="absolute -left-12 top-1/2 w-24 h-[1px] bg-gradient-to-l from-white/20 to-transparent" />
        </motion.div>
                    </div >
                </section >

        {/* --- Call to Action --- */ }
        < section className = "py-32 px-4 text-center relative" >
            <div className="max-w-4xl mx-auto space-y-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <h2 className="text-4xl md:text-6xl font-orbitron font-bold mb-8">Ready to Secure Your Vote?</h2>
                    <p className="text-xl text-white/50 mb-12">
                        Join the network and let the swarm protect your governance participation.
                    </p>

                    <button className="group relative px-8 py-4 bg-white text-black font-bold font-orbitron tracking-wider text-lg rounded-full overflow-hidden hover:scale-105 transition-transform">
                        <div className="absolute inset-0 bg-gradient-to-r from-neon-orchid to-electric-cyan opacity-0 group-hover:opacity-100 transition-opacity" />
                        <span className="relative z-10 group-hover:text-white transition-colors">LAUNCH DASHBOARD</span>
                    </button>
                </motion.div>
            </div>
                </section >

        {/* --- Footer --- */ }
        < footer className = "py-12 border-t border-white/10 text-center text-white/30 text-sm font-mono" >
            <p>SENTINEL ORCHESTRATOR NETWORK // v2.0.0</p>
                </footer >

            </div >
        </main >
    );
}
