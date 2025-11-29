"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { MatrixTerminal } from "@/components/MatrixTerminal";
import { RadarScan } from "@/components/RadarScan";
import { AgentEconomy } from "@/components/AgentEconomy";
import { Shield, Activity, Globe, Cpu, Wifi, Terminal } from "lucide-react";

// Mock Data - Strictly following PROJECT_IDEA.md narrative
const MOCK_LOGS = [
    { id: "1", agent: "SENTINEL", message: "Analyzing OpCodes... 127 Instructions Parsed.", type: "info", timestamp: Date.now() },
    { id: "2", agent: "SENTINEL", message: "Protocol: Plutus V3 Compliant ✓", type: "success", timestamp: Date.now() + 800 },
    { id: "3", agent: "SENTINEL", message: "ALERT: Missing Validity Interval (TTL). Vulnerable to Replay.", type: "warning", timestamp: Date.now() + 1500 },
    { id: "4", agent: "SENTINEL", message: "Action: HIRE_REQUEST @ORACLE-01. Escrow: 1.0 ₳", type: "action", timestamp: Date.now() + 2200 },
    { id: "5", agent: "ORACLE", message: "OFFER_ACCEPTED. Initiating Multi-Node Scan (5 targets)...", type: "info", timestamp: Date.now() + 3500 },
    { id: "6", agent: "ORACLE", message: "Scanning: IOG (Mainnet), Emurgo, CF, Coinbase...", type: "info", timestamp: Date.now() + 4500 },
    { id: "7", agent: "ORACLE", message: "CRITICAL: User Node on Minority Fork (30% Weight).", type: "error", timestamp: Date.now() + 6000 },
    { id: "8", agent: "ORACLE", message: "Evidence: Block Height Divergence (-30 blocks).", type: "error", timestamp: Date.now() + 6500 },
    { id: "9", agent: "MIDNIGHT", message: "Generating ZK-Proof of Threat...", type: "info", timestamp: Date.now() + 7500 },
    { id: "10", agent: "MIDNIGHT", message: "Proof Verified: 0xA7F2... (Privacy Preserved)", type: "success", timestamp: Date.now() + 9000 },
    { id: "11", agent: "SENTINEL", message: "VERDICT: UNSAFE_FORK. TRANSACTION BLOCKED.", type: "error", timestamp: Date.now() + 9500 },
] as const;

interface LogEntry {
    id: string;
    agent: "SENTINEL" | "ORACLE" | "MIDNIGHT";
    message: string;
    type: "info" | "warning" | "error" | "success" | "action";
    timestamp: number;
}

// Tech Decoration Component
const TechCorner = ({ className }: { className?: string }) => (
    <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M1 1V6M1 1H6" stroke="currentColor" strokeWidth="2" />
    </svg>
);

export default function Dashboard() {
    const router = useRouter();
    const [scanState, setScanState] = useState<"IDLE" | "SCANNING" | "VERDICT">("IDLE");
    const [verdict] = useState<"SAFE" | "DANGER">("DANGER"); // Default to Danger for demo
    const [logs, setLogs] = useState<LogEntry[]>([]);

    const startScan = () => {
        setScanState("SCANNING");
        setLogs([]);

        // Simulate log stream
        let delay = 0;
        MOCK_LOGS.forEach((log) => {
            // Calculate relative delay based on timestamps in MOCK_LOGS
            const relativeDelay = log.timestamp - MOCK_LOGS[0].timestamp;
            delay = relativeDelay;

            setTimeout(() => {
                setLogs((prev) => [...prev, { ...log, id: Math.random().toString(), timestamp: Date.now() }]);
            }, delay);
        });

        // Redirect to verdict page
        setTimeout(() => {
            router.push(`/verdict?status=${verdict}`);
        }, delay + 1500);
    };

    return (
        <main className="min-h-screen bg-obsidian-core text-ghost-white overflow-hidden relative selection:bg-neon-orchid/30 pt-24 pb-8 px-4 md:px-8">
            {/* HUD Grid Background */}
            <div className="fixed inset-0 bg-[linear-gradient(rgba(0,245,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] -z-10" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,0,0,0)_0%,rgba(0,0,0,0.8)_100%)] -z-10" />

            {/* Dashboard Grid */}
            <div className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-8rem)]">

                {/* Left Column: Controls & Input */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Header Card */}
                    <Card className="p-6 bg-black/40 border-white/10 backdrop-blur-xl relative overflow-hidden group">
                        <TechCorner className="absolute top-2 left-2 text-neon-orchid/50" />
                        <TechCorner className="absolute top-2 right-2 rotate-90 text-neon-orchid/50" />
                        <TechCorner className="absolute bottom-2 right-2 rotate-180 text-neon-orchid/50" />
                        <TechCorner className="absolute bottom-2 left-2 -rotate-90 text-neon-orchid/50" />

                        <div className="absolute inset-0 bg-gradient-to-r from-neon-orchid/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <div className="relative z-10">
                            <div className="flex items-center gap-3 mb-2">
                                <Shield className="w-6 h-6 text-neon-orchid" />
                                <h2 className="font-orbitron font-bold text-xl tracking-wider">SENTINEL CONTROL</h2>
                            </div>
                            <p className="text-xs text-white/50 font-mono">SYSTEM READY // WAITING FOR INPUT</p>
                        </div>
                    </Card>

                    {/* Input Area */}
                    <Card className="flex-1 p-6 bg-black/40 border-white/10 backdrop-blur-xl flex flex-col gap-4 relative">
                        <div className="flex items-center justify-between text-xs font-mono text-electric-cyan uppercase tracking-wider">
                            <span>Transaction Payload</span>
                            <span className="flex items-center gap-2">
                                <Terminal className="w-3 h-3" />
                                CBOR
                            </span>
                        </div>
                        <div className="relative flex-1 group">
                            <textarea
                                className="w-full h-full bg-black/50 border border-white/10 rounded-lg p-4 font-mono text-sm text-white/80 focus:outline-none focus:border-neon-orchid/50 transition-colors resize-none custom-scrollbar"
                                placeholder="Paste raw transaction CBOR here..."
                                disabled={scanState !== "IDLE"}
                            />
                            <div className="absolute inset-0 border border-neon-orchid/0 group-hover:border-neon-orchid/20 pointer-events-none rounded-lg transition-colors" />
                        </div>

                        <Button
                            className="w-full h-16 text-lg font-orbitron tracking-widest relative overflow-hidden"
                            onClick={startScan}
                            disabled={scanState !== "IDLE"}
                            isLoading={scanState === "SCANNING"}
                        >
                            <div className="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay" />
                            {scanState === "IDLE" ? "INITIATE SCAN" : "SCANNING..."}
                        </Button>
                    </Card>

                    {/* System Status */}
                    <div className="grid grid-cols-2 gap-4">
                        <Card className="p-4 bg-electric-cyan/5 border-electric-cyan/20 flex flex-col justify-between h-32 relative overflow-hidden">
                            <div className="absolute -right-4 -top-4 w-16 h-16 bg-electric-cyan/20 rounded-full blur-xl" />
                            <div className="flex justify-between items-start relative z-10">
                                <Globe className="w-5 h-5 text-electric-cyan" />
                                <div className="w-2 h-2 bg-electric-cyan rounded-full animate-pulse" />
                            </div>
                            <div className="relative z-10">
                                <div className="text-2xl font-orbitron font-bold">99.9%</div>
                                <div className="text-[10px] text-white/50 uppercase tracking-wider">Network Uptime</div>
                            </div>
                        </Card>
                        <Card className="p-4 bg-plasma-pink/5 border-plasma-pink/20 flex flex-col justify-between h-32 relative overflow-hidden">
                            <div className="absolute -right-4 -top-4 w-16 h-16 bg-plasma-pink/20 rounded-full blur-xl" />
                            <div className="flex justify-between items-start relative z-10">
                                <Cpu className="w-5 h-5 text-plasma-pink" />
                                <Wifi className="w-4 h-4 text-plasma-pink/50" />
                            </div>
                            <div className="relative z-10">
                                <div className="text-2xl font-orbitron font-bold">1,247</div>
                                <div className="text-[10px] text-white/50 uppercase tracking-wider">Active Agents</div>
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Middle Column: Visualization */}
                <div className="lg:col-span-5 flex flex-col gap-6 relative">
                    <Card className="flex-1 bg-black/60 border-white/10 backdrop-blur-xl relative overflow-hidden p-1">
                        <TechCorner className="absolute top-2 left-2 text-white/20" />
                        <TechCorner className="absolute top-2 right-2 rotate-90 text-white/20" />
                        <TechCorner className="absolute bottom-2 right-2 rotate-180 text-white/20" />
                        <TechCorner className="absolute bottom-2 left-2 -rotate-90 text-white/20" />

                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,245,255,0.05)_0%,transparent_70%)]" />

                        <div className="relative h-full rounded-xl overflow-hidden bg-black/40">
                            <AnimatePresence mode="wait">
                                {scanState === "IDLE" ? (
                                    <motion.div
                                        key="radar"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="h-full flex flex-col items-center justify-center"
                                    >
                                        <RadarScan />
                                        <p className="mt-8 text-xs font-mono text-white/30 tracking-[0.2em] animate-pulse">SCANNING FOR THREATS</p>
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="terminal"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="h-full"
                                    >
                                        <MatrixTerminal logs={logs} isActive={true} />
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </Card>
                </div>

                {/* Right Column: Agent Economy */}
                <div className="lg:col-span-3 flex flex-col gap-6">
                    <Card className="flex-1 bg-black/40 border-white/10 backdrop-blur-xl p-6 flex flex-col relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-warning/5 rounded-full blur-3xl -z-10" />
                        <h3 className="font-orbitron font-bold text-sm tracking-wider mb-6 flex items-center gap-2">
                            <Activity className="w-4 h-4 text-amber-warning" />
                            AGENT SWARM
                        </h3>
                        <div className="flex-1 flex items-center justify-center">
                            <AgentEconomy />
                        </div>
                        <div className="mt-6 space-y-3">
                            {[
                                { label: "Sentinel", status: "Active", color: "text-neon-orchid" },
                                { label: "Oracle", status: "Standby", color: "text-electric-cyan" },
                                { label: "Midnight", status: "Offline", color: "text-amber-warning" }
                            ].map((agent, idx) => (
                                <div key={idx} className="flex items-center justify-between text-xs font-mono border-b border-white/5 pb-2 last:border-0">
                                    <span className={agent.color}>{agent.label}</span>
                                    <span className="text-white/50">{agent.status}</span>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>
            </div>

            {/* Overlays */}
            {/* Verdict is now handled on a separate page */}
        </main>
    );
}
