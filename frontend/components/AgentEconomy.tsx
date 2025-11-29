import React from "react";
import { motion } from "framer-motion";
import { Card } from "./ui/Card";

export const AgentEconomy = () => {
    return (
        <Card className="h-[280px] flex items-center justify-center relative overflow-visible">
            <div className="absolute inset-0 bg-gradient-to-br from-obsidian-core to-void-gray opacity-50 rounded-2xl overflow-hidden" />

            {/* Nodes Container */}
            <div className="relative z-10 w-full max-w-sm h-[200px]">
                {/* Sentinel (Top Center) */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 flex flex-col items-center z-20">
                    <div className="w-12 h-12 rounded-lg bg-neon-orchid/20 border border-neon-orchid flex items-center justify-center shadow-[0_0_15px_rgba(255,0,110,0.3)] backdrop-blur-sm">
                        <div className="w-3 h-3 bg-neon-orchid rounded-full animate-pulse" />
                    </div>
                    <span className="text-xs text-neon-orchid mt-2 font-mono font-bold tracking-wider bg-black/50 px-2 py-0.5 rounded">SENTINEL</span>
                </div>

                {/* Oracle (Bottom Left) */}
                <div className="absolute bottom-0 left-4 flex flex-col items-center z-20">
                    <div className="w-12 h-12 rounded-full bg-electric-cyan/20 border border-electric-cyan flex items-center justify-center shadow-[0_0_15px_rgba(0,245,255,0.3)] backdrop-blur-sm">
                        <div className="w-3 h-3 bg-electric-cyan rounded-full animate-pulse" />
                    </div>
                    <span className="text-xs text-electric-cyan mt-2 font-mono font-bold tracking-wider bg-black/50 px-2 py-0.5 rounded">ORACLE</span>
                </div>

                {/* Midnight (Bottom Right) */}
                <div className="absolute bottom-0 right-4 flex flex-col items-center z-20">
                    <div className="w-12 h-12 rounded-full bg-amber-warning/20 border border-amber-warning flex items-center justify-center shadow-[0_0_15px_rgba(255,182,39,0.3)] backdrop-blur-sm">
                        <div className="w-3 h-3 bg-amber-warning rounded-full animate-pulse" />
                    </div>
                    <span className="text-xs text-amber-warning mt-2 font-mono font-bold tracking-wider bg-black/50 px-2 py-0.5 rounded">MIDNIGHT</span>
                </div>

                {/* Connections Layer */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none overflow-visible">
                    <defs>
                        <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#FF006E" />
                            <stop offset="100%" stopColor="#00F5FF" />
                        </linearGradient>
                        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#FF006E" />
                            <stop offset="100%" stopColor="#FFB627" />
                        </linearGradient>
                        <linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#00F5FF" />
                            <stop offset="100%" stopColor="#FFB627" />
                        </linearGradient>
                    </defs>

                    {/* Sentinel -> Oracle (Adjusted coordinates based on new layout) */}
                    <motion.path
                        d="M 192 48 L 40 170"
                        stroke="url(#grad1)"
                        strokeWidth="2"
                        fill="none"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse" }}
                    />
                    {/* Sentinel -> Midnight */}
                    <motion.path
                        d="M 192 48 L 344 170"
                        stroke="url(#grad2)"
                        strokeWidth="2"
                        fill="none"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        transition={{ duration: 1.5, delay: 0.5, repeat: Infinity, repeatType: "reverse" }}
                    />
                    {/* Oracle -> Midnight */}
                    <motion.path
                        d="M 40 170 L 344 170"
                        stroke="url(#grad3)"
                        strokeWidth="2"
                        fill="none"
                        strokeDasharray="4 4"
                        initial={{ opacity: 0.3 }}
                        animate={{ opacity: 0.6 }}
                    />
                </svg>

                {/* Floating Particles (Money Flow) */}
                <motion.div
                    className="absolute w-2 h-2 bg-plasma-pink rounded-full shadow-[0_0_8px_#D81159] z-10"
                    animate={{ offsetDistance: "100%" }}
                    style={{ offsetPath: "path('M 192 48 L 40 170')" }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
            </div>
        </Card>
    );
};
