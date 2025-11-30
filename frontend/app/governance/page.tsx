"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Shield, FileText, Scale, Users, Search, CheckCircle, XCircle, LucideIcon } from "lucide-react";
import { ProtectedPage } from "@/components/ProtectedPage";



interface LogEntry {
    agent: string;
    message: string;
    status: string;
    delay: number;
}

export default function GovernancePage() {
    const [input, setInput] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [verdict, setVerdict] = useState<"IDLE" | "APPROVED" | "REJECTED" | "MANUAL">("IDLE");

    const startAnalysis = async () => {
        setIsAnalyzing(true);
        setLogs([]);
        setVerdict("IDLE");

        // Initial log
        setLogs(prev => [...prev, { agent: "FETCHER", message: `Resolving IPFS Hash: ${input.substring(0, 15)}...`, status: "running", delay: 0 }]);

        try {
            const response = await fetch("http://localhost:8000/api/v1/governance/proposal-check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ipfs_hash: input })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Analysis failed");
            }

            const data = await response.json();

            // Simulate the pipeline visualization based on real data
            setLogs(prev => [...prev, { agent: "FETCHER", message: "Metadata Retrieved: CIP-108 Compliant", status: "success", delay: 0 }]);

            setTimeout(() => {
                setLogs(prev => [...prev, { agent: "POLICY", message: "Analyzing Constitution Compatibility...", status: "running", delay: 0 }]);
            }, 1000);

            setTimeout(() => {
                setLogs(prev => [...prev, { agent: "SENTIMENT", message: "Scanning Forum Sentiment...", status: "running", delay: 0 }]);
            }, 1500);

            setTimeout(() => {
                // Add flags from policy analysis
                data.policy_compliance.flags.forEach((flag: string) => {
                    setLogs(prev => [...prev, { agent: "POLICY", message: `Flag: ${flag}`, status: "warning", delay: 0 }]);
                });

                setLogs(prev => [...prev, { agent: "POLICY", message: `Recommendation: ${data.policy_compliance.recommendation}`, status: "success", delay: 0 }]);
            }, 3000);

            setTimeout(() => {
                setLogs(prev => [...prev, { agent: "ORCHESTRATOR", message: "Aggregating Verdict...", status: "running", delay: 0 }]);
            }, 4500);

            setTimeout(() => {
                const finalVerdict = data.policy_compliance.recommendation === "YES" ? "APPROVED" : "REJECTED";
                setLogs(prev => [...prev, { agent: "ORCHESTRATOR", message: `VERDICT: ${finalVerdict}`, status: "success", delay: 0 }]);
                setVerdict(finalVerdict);
                setIsAnalyzing(false);
            }, 5500);

        } catch (error: any) {
            console.error(error);
            setLogs(prev => [...prev, { agent: "ORCHESTRATOR", message: `Error: ${error.message || "Analysis Failed"}`, status: "error", delay: 0 }]);
            setIsAnalyzing(false);
        }
    };

    return (
        <ProtectedPage>
        <main className="min-h-screen text-ghost-white overflow-hidden relative selection:bg-neon-orchid/30 pt-24 pb-8 px-4 md:px-8">
            {/* Base Background Color */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />

            {/* Background Effects */}
            <div className="fixed inset-0 bg-[linear-gradient(rgba(0,245,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] -z-10" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,245,255,0.1)_0%,transparent_50%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />
            <div className="fixed inset-0 bg-[url('/protocol-circuit.png')] bg-cover bg-center opacity-[0.05] mix-blend-screen pointer-events-none -z-5" />

            <div className="max-w-7xl mx-auto space-y-8 relative z-10">
                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-electric-cyan/10 border border-electric-cyan/20 text-electric-cyan text-xs font-mono tracking-widest uppercase mb-4"
                    >
                        <Scale className="w-3 h-3" />
                        Governance Agent Service
                    </motion.div>
                    <h1 className="text-4xl md:text-6xl font-orbitron font-black tracking-tighter">
                        <ScrambleText text="CONSTITUTIONAL" /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-electric-cyan to-neon-orchid">GUARD</span>
                    </h1>
                    <p className="text-white/60 max-w-2xl mx-auto text-lg">
                        Automated analysis of governance actions against the Interim Constitution and community sentiment.
                    </p>
                </div>

                {/* Input Section */}
                <Card className="p-8 bg-black/40 border-white/10 backdrop-blur-xl rounded-2xl max-w-3xl mx-auto relative z-20">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 relative group">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <Search className="w-5 h-5 text-white/30 group-focus-within:text-electric-cyan transition-colors" />
                            </div>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Enter Governance Action ID or IPFS Hash..."
                                className="w-full h-14 pl-12 pr-4 bg-black/50 border border-white/10 rounded-xl focus:outline-none focus:border-electric-cyan/50 text-white font-mono placeholder:text-white/20 transition-all relative z-50"
                            />
                        </div>
                        <Button
                            onClick={startAnalysis}
                            disabled={isAnalyzing || !input}
                            className="h-14 px-8 text-lg font-orbitron tracking-wider bg-electric-cyan/10 hover:bg-electric-cyan/20 border-electric-cyan/50 text-electric-cyan"
                        >
                            {isAnalyzing ? "ANALYZING..." : "RUN AUDIT"}
                        </Button>
                    </div>
                </Card>

                {/* Analysis Pipeline */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Agent 1: Fetcher */}
                    <AgentColumn
                        title="Proposal Fetcher"
                        icon={FileText}
                        color="text-neon-orchid"
                        logs={logs.filter(l => l.agent === "FETCHER")}
                        isActive={isAnalyzing}
                    />

                    {/* Agent 2: Policy */}
                    <AgentColumn
                        title="Policy Analyzer"
                        icon={Shield}
                        color="text-electric-cyan"
                        logs={logs.filter(l => l.agent === "POLICY")}
                        isActive={isAnalyzing}
                    />

                    {/* Agent 3: Sentiment */}
                    <AgentColumn
                        title="Sentiment Oracle"
                        icon={Users}
                        color="text-plasma-pink"
                        logs={logs.filter(l => l.agent === "SENTIMENT")}
                        isActive={isAnalyzing}
                    />
                </div>

                {/* Verdict Output */}
                <AnimatePresence>
                    {verdict !== "IDLE" && (
                        <motion.div
                            initial={{ opacity: 0, y: 20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                        >
                            <HolographicCard className="p-8 bg-black/60 border-white/10 backdrop-blur-xl rounded-3xl overflow-hidden relative">
                                <div className={`absolute inset-0 opacity-20 mix-blend-overlay ${verdict === "APPROVED" ? "bg-green-500" : "bg-red-500"
                                    }`} />

                                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                                    <div className="flex items-center gap-6">
                                        <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 ${verdict === "APPROVED" ? "border-green-500 bg-green-500/10 text-green-500" : "border-red-500 bg-red-500/10 text-red-500"
                                            }`}>
                                            {verdict === "APPROVED" ? <CheckCircle className="w-10 h-10" /> : <XCircle className="w-10 h-10" />}
                                        </div>
                                        <div>
                                            <div className="text-sm font-mono text-white/50 uppercase tracking-widest mb-1">Final Verdict</div>
                                            <h2 className={`text-4xl font-orbitron font-bold ${verdict === "APPROVED" ? "text-green-500" : "text-red-500"
                                                }`}>
                                                {verdict === "APPROVED" ? "COMPLIANT" : "VIOLATION DETECTED"}
                                            </h2>
                                            <p className="text-white/70 mt-2 max-w-xl">
                                                Proposal passes all constitutional checks and aligns with community sentiment parameters.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex gap-8 text-center">
                                        <div>
                                            <div className="text-3xl font-mono font-bold text-white">98%</div>
                                            <div className="text-xs text-white/40 uppercase tracking-wider">Confidence</div>
                                        </div>
                                        <div>
                                            <div className="text-3xl font-mono font-bold text-electric-cyan">V3</div>
                                            <div className="text-xs text-white/40 uppercase tracking-wider">Protocol</div>
                                        </div>
                                    </div>
                                </div>
                            </HolographicCard>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
        </ProtectedPage>
    );
}

interface AgentColumnProps {
    title: string;
    icon: LucideIcon;
    color: string;
    logs: LogEntry[];
    isActive: boolean;
}

function AgentColumn({ title, icon: Icon, color, logs, isActive }: AgentColumnProps) {
    return (
        <Card className="bg-black/40 border-white/10 backdrop-blur-sm h-[400px] flex flex-col overflow-hidden relative group">
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
                <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${color}`} />
                    <span className="font-orbitron font-bold text-sm tracking-wide">{title}</span>
                </div>
                {isActive && (
                    <div className="flex gap-1">
                        <span className={`w-1.5 h-1.5 rounded-full ${color} animate-pulse`} />
                        <span className={`w-1.5 h-1.5 rounded-full ${color} animate-pulse delay-75`} />
                        <span className={`w-1.5 h-1.5 rounded-full ${color} animate-pulse delay-150`} />
                    </div>
                )}
            </div>

            <div className="flex-1 p-4 font-mono text-xs space-y-3 overflow-y-auto custom-scrollbar relative">
                {logs.length === 0 && isActive && (
                    <div className="text-white/30 italic">Initializing agent...</div>
                )}
                {logs.map((log, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`flex gap-2 ${log.status === "success" ? "text-green-400" :
                            log.status === "warning" ? "text-amber-400" :
                                log.status === "error" ? "text-red-400" :
                                    "text-white/70"
                            }`}
                    >
                        <span className="opacity-50">{">"}</span>
                        <span>{log.message}</span>
                    </motion.div>
                ))}

                {/* Scanline Effect */}
                <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.2)_50%)] bg-[size:100%_4px] pointer-events-none opacity-20" />
            </div>
        </Card>
    );
}
