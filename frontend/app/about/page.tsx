"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Card } from "@/components/ui/Card";
import { AgentEconomy } from "@/components/AgentEconomy";
import { Shield, AlertTriangle, CheckCircle, Zap, Search, Lock } from "lucide-react";

// Tech Decoration Component
const TechCorner = ({ className }: { className?: string }) => (
    <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M1 1V6M1 1H6" stroke="currentColor" strokeWidth="2" />
    </svg>
);

export default function AboutPage() {
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"],
    });

    const opacityHero = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
    const scaleHero = useTransform(scrollYProgress, [0, 0.2], [1, 0.9]);

    return (
        <main ref={containerRef} className="min-h-[300vh] bg-obsidian-core text-ghost-white overflow-x-hidden relative selection:bg-neon-orchid/30">
            {/* Fixed Background */}
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_0%,#1E2738_0%,#0A0E1A_100%)] -z-20" />
            <div className="fixed inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px] -z-10 [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_80%)]" />

            {/* Hero Section */}
            <section className="h-screen flex flex-col items-center justify-center px-4 sticky top-0">
                <motion.div
                    style={{ opacity: opacityHero, scale: scaleHero }}
                    className="text-center space-y-8 max-w-4xl"
                >
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-4"
                    >
                        <Shield className="w-4 h-4 text-neon-orchid" />
                        <span className="text-xs font-mono tracking-widest text-neon-orchid uppercase">Protocol Architecture</span>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1, delay: 0.2 }}
                        className="text-6xl md:text-8xl font-orbitron font-black leading-tight tracking-tighter"
                    >
                        THE <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-orchid to-electric-cyan">INVISIBLE</span><br />
                        GUARDIAN
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4 }}
                        className="text-xl text-white/60 max-w-2xl mx-auto leading-relaxed"
                    >
                        How a swarm of autonomous agents protects your assets from the hidden dangers of the Voltaire era.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1, duration: 1 }}
                        className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
                    >
                        <span className="text-[10px] font-mono uppercase tracking-widest text-white/30">Scroll to Learn</span>
                        <div className="w-[1px] h-12 bg-gradient-to-b from-neon-orchid to-transparent" />
                    </motion.div>
                </motion.div>
            </section>

            {/* Content Sections (Overlapping) */}
            <div className="relative z-10 mt-[100vh] space-y-[50vh] pb-[50vh]">

                {/* Section 1: The Problem */}
                <section className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        className="space-y-6"
                    >
                        <div className="w-12 h-12 rounded-2xl bg-amber-warning/10 flex items-center justify-center border border-amber-warning/20 shadow-[0_0_30px_rgba(255,193,7,0.2)]">
                            <AlertTriangle className="w-6 h-6 text-amber-warning" />
                        </div>
                        <h2 className="text-4xl md:text-5xl font-orbitron font-bold">The Governance Fog</h2>
                        <p className="text-lg text-white/70 leading-relaxed">
                            In the Voltaire era, governance actions are on-chain transactions. But what if the chain you&apos;re on isn&apos;t the real one?
                            <br /><br />
                            <strong>Chain Splits</strong> create &quot;ghost chains&quot; where your signature can be replayed or your vote lost. Wallets are blind to this—they just see a connection.
                        </p>
                    </motion.div>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true, margin: "-20%" }}
                    >
                        <Card className="p-8 bg-black/60 border-white/10 backdrop-blur-xl relative overflow-hidden group">
                            <TechCorner className="absolute top-4 left-4 text-amber-warning/50" />
                            <TechCorner className="absolute top-4 right-4 rotate-90 text-amber-warning/50" />
                            <TechCorner className="absolute bottom-4 right-4 rotate-180 text-amber-warning/50" />
                            <TechCorner className="absolute bottom-4 left-4 -rotate-90 text-amber-warning/50" />

                            <div className="absolute inset-0 bg-gradient-to-br from-amber-warning/5 to-transparent opacity-50" />
                            <div className="relative z-10 flex flex-col items-center gap-4 text-center">
                                <div className="w-full h-48 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center relative overflow-hidden">
                                    <div className="absolute inset-0 flex items-center justify-center gap-8 opacity-50">
                                        <div className="w-1 h-32 bg-white/20" />
                                        <div className="w-1 h-32 bg-white/20 rotate-12 origin-bottom" />
                                    </div>
                                    <span className="font-mono text-amber-warning bg-black/50 px-3 py-1 rounded border border-amber-warning/30 animate-pulse">FORK DETECTED</span>
                                </div>
                                <p className="text-sm text-white/50 font-mono">Simulated Chain Split Scenario</p>
                            </div>
                        </Card>
                    </motion.div>
                </section>

                {/* Section 2: The Swarm */}
                <section className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true, margin: "-20%" }}
                        className="order-2 md:order-1"
                    >
                        <div className="relative">
                            <div className="absolute inset-0 bg-neon-orchid/20 blur-[100px] rounded-full" />
                            <AgentEconomy />
                        </div>
                    </motion.div>
                    <motion.div
                        initial={{ opacity: 0, x: 50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        className="space-y-6 order-1 md:order-2"
                    >
                        <div className="w-12 h-12 rounded-2xl bg-neon-orchid/10 flex items-center justify-center border border-neon-orchid/20 shadow-[0_0_30px_rgba(255,0,110,0.2)]">
                            <Zap className="w-6 h-6 text-neon-orchid" />
                        </div>
                        <h2 className="text-4xl md:text-5xl font-orbitron font-bold">Enter The Swarm</h2>
                        <p className="text-lg text-white/70 leading-relaxed">
                            Sentinel is a <strong>Pre-Signing Middleware</strong>. Before you sign, a swarm of AI agents activates to verify the reality of your connection.
                        </p>
                        <ul className="space-y-4">
                            {[
                                { name: "Sentinel", role: "Orchestrator", desc: "Parses intent & hires specialists", color: "text-neon-orchid" },
                                { name: "Oracle", role: "Scout", desc: "Verifies block height across 50+ nodes", color: "text-electric-cyan" },
                                { name: "Midnight", role: "Ghost", desc: "Generates ZK-proofs of threats", color: "text-amber-warning" }
                            ].map((agent, idx) => (
                                <li key={idx} className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group">
                                    <div className={`font-bold font-mono ${agent.color} group-hover:scale-110 transition-transform`}>{agent.name}</div>
                                    <div className="w-[1px] h-4 bg-white/20" />
                                    <div className="text-sm text-white/80">
                                        <span className="font-bold">{agent.role}</span>: {agent.desc}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                </section>

                {/* Section 3: The Workflow */}
                <section className="max-w-4xl mx-auto px-4 text-center space-y-16">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                    >
                        <h2 className="text-4xl md:text-5xl font-orbitron font-bold mb-6">Defense Protocol</h2>
                        <p className="text-white/60 max-w-2xl mx-auto">The automated sequence that executes in milliseconds to protect your transaction.</p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                            { icon: Search, title: "1. Scan", desc: "Oracle agents ping global nodes to verify consensus weight." },
                            { icon: Lock, title: "2. Verify", desc: "Midnight agents generate ZK-proofs if anomalies are found." },
                            { icon: CheckCircle, title: "3. Act", desc: "Sentinel blocks the transaction or greenlights it." }
                        ].map((step, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true, margin: "-20%" }}
                                transition={{ delay: idx * 0.2 }}
                            >
                                <Card className="p-8 h-full bg-white/5 border-white/10 hover:bg-white/10 transition-colors group relative overflow-hidden">
                                    <TechCorner className="absolute top-2 left-2 text-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <TechCorner className="absolute bottom-2 right-2 rotate-180 text-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />

                                    <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-white/10 to-transparent flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-[0_0_20px_rgba(255,255,255,0.1)]">
                                        <step.icon className="w-8 h-8 text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold font-orbitron mb-4">{step.title}</h3>
                                    <p className="text-white/60 leading-relaxed">{step.desc}</p>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </section>

            </div>
        </main>
    );
}
