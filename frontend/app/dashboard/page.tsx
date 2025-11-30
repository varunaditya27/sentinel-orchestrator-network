"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { MatrixTerminal, LogEntry } from "@/components/MatrixTerminal";
import { RadarScan } from "@/components/RadarScan";
import { AgentEconomy } from "@/components/AgentEconomy";
import { ComplianceHUD } from "@/components/ComplianceHUD";
import { HyperspaceTransition } from "@/components/HyperspaceTransition";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { Shield, Activity, Globe, Cpu, Wifi, Terminal } from "lucide-react";
import { ProtectedPage } from "@/components/ProtectedPage";





// Tech Decoration Component
const TechCorner = ({ className }: { className?: string }) => (
    <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M1 1V6M1 1H6" stroke="currentColor" strokeWidth="2" />
    </svg>
);

export default function Dashboard() {
    const router = useRouter();
    const [scanState, setScanState] = useState<"IDLE" | "SCANNING" | "COMPLETE" | "VERDICT">("IDLE");
    const [logs, setLogs] = useState<LogEntry[]>([]);

    const [inputPayload, setInputPayload] = useState("");
    const [systemStatus, setSystemStatus] = useState({
        sentinel: "Active",
        oracle: "Standby",
        hydra: "Offline",
        midnight: "Offline",
        network_uptime: "99.9%",
        active_agents: 3
    });
    const [randomBytes, setRandomBytes] = useState<string[]>([]);
    const [paymentActive, setPaymentActive] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [scanHistory, setScanHistory] = useState<any[]>([]);

    const fetchHistory = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/v1/scans/history");
            if (res.ok) {
                const data = await res.json();
                setScanHistory(data);
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
    };

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/v1/system/status");
                if (res.ok) {
                    const data = await res.json();
                    setSystemStatus(data);
                }
            } catch (e) {
                console.error("Failed to fetch system status", e);
            }
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        setRandomBytes(Array.from({ length: 400 }).map(() =>
            Math.floor(Math.random() * 255).toString(16).padStart(2, '0').toUpperCase()
        ));
    }, []);

    useEffect(() => {
        const lastLog = logs[logs.length - 1];
        if (lastLog?.message.includes("HIRE_REQUEST")) {
            setPaymentActive(true);
            const timer = setTimeout(() => setPaymentActive(false), 2000);
            return () => clearTimeout(timer);
        }
    }, [logs]);

    const startScan = async () => {
        if (!scanState || scanState === "SCANNING") return;

        setScanState("SCANNING");
        setLogs([]);

        try {
            // Determine if input is Policy ID (hex, 56 chars) or CBOR
            const isPolicyId = /^[0-9a-fA-F]{56}$/.test(inputPayload.trim());

            const payload = {
                user_tip: 1000,
                ...(isPolicyId ? { policy_id: inputPayload.trim() } : { tx_cbor: inputPayload.trim() })
            };

            // 1. Call API to start scan
            const response = await fetch("http://localhost:8000/api/v1/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            const taskId = data.task_id;

            // 2. Connect to WebSocket for results
            const ws = new WebSocket(`ws://localhost:8000/ws/scan/${taskId}`);

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                const payload = message.payload;

                if (payload) {
                    // Add log entry
                    setLogs(prev => [...prev, {
                        id: Math.random().toString(),
                        agent: "SENTINEL",
                        message: `VERDICT: ${payload.verdict} (${payload.reason})`,
                        type: payload.verdict === "SAFE" ? "success" : "error",
                        timestamp: Date.now()
                    }]);

                    // If verdict received, redirect
                    if (payload.verdict) {
                        setTimeout(() => {
                            setScanState("VERDICT");
                            // Redirect to verdict page with status and task ID
                            router.push(`/verdict?status=${payload.verdict}&taskId=${data.task_id}`);
                        }, 1500);
                        ws.close();
                    }
                }
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                setScanState("IDLE");
            };

        } catch (error) {
            console.error("Scan failed:", error);
            setScanState("IDLE");
        }
    };

    return (
        <ProtectedPage>
        <main className="min-h-screen text-ghost-white overflow-hidden relative selection:bg-neon-orchid/30 pt-24 pb-8 px-4 md:px-8">
            {/* Base Background Color */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />

            {/* HUD Grid Background */}
            <div className="fixed inset-0 bg-[linear-gradient(rgba(0,245,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] -z-10" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,0,0,0)_0%,rgba(0,0,0,0.8)_100%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />

            {/* Subtle Solution BG Overlay for "Safe" vibes (always present but subtle) */}
            <div className="fixed inset-0 bg-[url('/solution-bg.png')] bg-cover bg-center opacity-[0.05] mix-blend-screen pointer-events-none -z-5" />

            {/* Dashboard Grid */}
            <div className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-8rem)]">

                {/* Left Column: Controls & Input */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Header Card */}
                    <HolographicCard className="p-6 bg-black/40 border-white/10 backdrop-blur-xl relative overflow-hidden group rounded-xl">
                        <TechCorner className="absolute top-2 left-2 text-neon-orchid/50" />
                        <TechCorner className="absolute top-2 right-2 rotate-90 text-neon-orchid/50" />
                        <TechCorner className="absolute bottom-2 right-2 rotate-180 text-neon-orchid/50" />
                        <TechCorner className="absolute bottom-2 left-2 -rotate-90 text-neon-orchid/50" />

                        <div className="absolute inset-0 bg-gradient-to-r from-neon-orchid/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <div className="relative z-10">
                            <div className="flex items-center gap-3 mb-2">
                                <Shield className="w-6 h-6 text-neon-orchid" />
                                <h2 className="font-orbitron font-bold text-xl tracking-wider">
                                    <ScrambleText text="SENTINEL CONTROL" />
                                </h2>
                            </div>
                            <p className="text-xs text-white/50 font-mono">SYSTEM READY // WAITING FOR INPUT</p>
                        </div>
                    </HolographicCard>

                    {/* Input Area */}
                    <Card className="flex-1 p-6 bg-black/40 border-white/10 backdrop-blur-xl flex flex-col gap-4 relative">
                        <div className="flex items-center justify-between text-xs font-mono text-electric-cyan uppercase tracking-wider">
                            <span>Transaction Payload</span>
                            <span className="flex items-center gap-2">
                                <Terminal className="w-3 h-3" />
                                CBOR
                            </span>
                        </div>
                        <div className="relative flex-1 group overflow-hidden rounded-lg">
                            {/* Living Input Background */}
                            <div className="absolute inset-0 opacity-10 pointer-events-none font-mono text-[10px] leading-3 text-neon-orchid overflow-hidden select-none">
                                {randomBytes.map((byte, i) => (
                                    <span key={i} className="inline-block w-4 text-center">
                                        {byte}
                                    </span>
                                ))}
                            </div>

                            <textarea
                                className="w-full h-full bg-black/50 border border-white/10 rounded-lg p-4 font-mono text-sm text-white/80 focus:outline-none focus:border-neon-orchid/50 transition-colors resize-none custom-scrollbar relative z-10 backdrop-blur-sm"
                                placeholder="Paste raw transaction CBOR here..."
                                disabled={scanState !== "IDLE"}
                                value={inputPayload}
                                onChange={(e) => setInputPayload(e.target.value)}
                            />

                            {/* Analysis Overlay */}
                            <AnimatePresence>
                                {scanState === "SCANNING" && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="absolute inset-0 bg-black/80 backdrop-blur-md z-20 flex flex-col items-center justify-center font-mono"
                                    >
                                        <div className="text-neon-orchid text-xs tracking-widest mb-2 animate-pulse">DECODING PAYLOAD</div>
                                        <div className="w-48 h-1 bg-white/10 rounded-full overflow-hidden">
                                            <motion.div
                                                className="h-full bg-neon-orchid"
                                                animate={{ width: ["0%", "100%"] }}
                                                transition={{ duration: 1.5, repeat: Infinity }}
                                            />
                                        </div>
                                        <div className="mt-2 text-[10px] text-white/50">
                                            {["PARSING_OPCODES", "CHECKING_SIGS", "VALIDATING_UTXO"].map((text, i) => (
                                                <motion.div
                                                    key={text}
                                                    initial={{ opacity: 0, y: 10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    transition={{ delay: i * 0.5, duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
                                                >
                                                    {text}...
                                                </motion.div>
                                            ))}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="absolute inset-0 border border-neon-orchid/0 group-hover:border-neon-orchid/20 pointer-events-none rounded-lg transition-colors z-30" />
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
                                <div className="text-2xl font-orbitron font-bold">{systemStatus.network_uptime}</div>
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
                                <div className="text-2xl font-orbitron font-bold">{systemStatus.active_agents}</div>
                                <div className="text-[10px] text-white/50 uppercase tracking-wider">Active Agents</div>
                            </div>
                        </Card>
                    </div>

                    {/* History Button */}
                    <Button variant="secondary" className="w-full" onClick={fetchHistory}>
                        VIEW SCAN HISTORY
                    </Button>
                </div>

                {/* Middle Column: Visualization */}
                <div className="lg:col-span-5 flex flex-col gap-6 relative">
                    <Card className="flex-1 bg-black/60 border-white/10 backdrop-blur-xl relative overflow-hidden p-1">
                        <TechCorner className="absolute top-2 left-2 text-white/20" />
                        <TechCorner className="absolute top-2 right-2 rotate-90 text-white/20" />
                        <TechCorner className="absolute bottom-2 left-2 -rotate-90 text-white/20" />

                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,245,255,0.05)_0%,transparent_70%)]" />

                        {/* Process BG for Scanning State */}
                        <motion.div
                            className="absolute inset-0 bg-[url('/process-bg.png')] bg-cover bg-center opacity-0 mix-blend-screen"
                            animate={{ opacity: scanState === "SCANNING" ? 0.1 : 0 }}
                            transition={{ duration: 1 }}
                        />

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
                                        <p className="mt-8 text-xs font-mono text-white/30 tracking-[0.2em] animate-pulse absolute bottom-8">SCANNING FOR THREATS</p>
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="terminal"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="h-full flex flex-col relative"
                                    >
                                        {/* Threat BG Overlay */}
                                        <div className="absolute inset-0 bg-[url('/threat-bg.png')] bg-cover bg-center opacity-10 mix-blend-overlay pointer-events-none" />

                                        {/* Split View: Terminal + Compliance HUD */}
                                        <div className="h-1/2 border-b border-white/10 relative z-10">
                                            <MatrixTerminal logs={logs} isActive={true} />
                                        </div>
                                        <div className="h-1/2 relative z-10">
                                            <ComplianceHUD isActive={true} />
                                        </div>
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
                            <AgentEconomy
                                activeAgent={
                                    logs.length > 0 ? logs[logs.length - 1].agent : null
                                }
                                paymentActive={paymentActive}
                            />
                        </div>
                        <div className="mt-6 space-y-3">
                            {[
                                { label: "Sentinel", status: systemStatus.sentinel, color: "text-neon-orchid" },
                                { label: "Oracle", status: systemStatus.oracle, color: "text-electric-cyan" },
                                { label: "Hydra", status: systemStatus.hydra, color: "text-plasma-pink" },
                                { label: "Midnight", status: systemStatus.midnight, color: "text-amber-warning" }
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
            <HyperspaceTransition isActive={scanState === "VERDICT"} />

            {/* History Modal */}
            <AnimatePresence>
                {showHistory && (
                    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                        <Card className="w-full max-w-2xl max-h-[80vh] flex flex-col bg-obsidian-core border-neon-orchid/50 relative overflow-hidden">
                            <div className="p-6 border-b border-white/10 flex justify-between items-center">
                                <h3 className="font-orbitron font-bold text-xl text-white">SCAN HISTORY</h3>
                                <Button variant="secondary" className="!p-2 rounded-full" onClick={() => setShowHistory(false)}>
                                    <Shield className="w-4 h-4" />
                                </Button>
                            </div>
                            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                                {scanHistory.length === 0 ? (
                                    <div className="text-center text-white/50 font-mono">No scans recorded yet.</div>
                                ) : (
                                    scanHistory.map((scan) => (
                                        <div key={scan.task_id} className="p-4 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center hover:bg-white/10 transition-colors cursor-pointer" onClick={() => router.push(`/verdict?status=${scan.verdict}&taskId=${scan.task_id}`)}>
                                            <div>
                                                <div className="text-xs text-white/50 font-mono mb-1">{new Date(scan.timestamp).toLocaleString()}</div>
                                                <div className="text-sm text-white font-mono truncate max-w-[300px]">{scan.policy_id || "Transaction Scan"}</div>
                                            </div>
                                            <div className={`px-3 py-1 rounded text-xs font-bold ${scan.verdict === "SAFE" ? "bg-electric-cyan/20 text-electric-cyan" : "bg-neon-orchid/20 text-neon-orchid"}`}>
                                                {scan.verdict || "UNKNOWN"}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </Card>
                    </div>
                )}
            </AnimatePresence>
        </main>
        </ProtectedPage>
    );
}
