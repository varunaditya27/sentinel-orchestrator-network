"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { TreasuryRiskGauge } from "@/components/TreasuryRiskGauge";
import { Coins, AlertTriangle, TrendingUp, ShieldAlert, Search } from "lucide-react";
import { ProtectedPage } from "@/components/ProtectedPage";

export default function TreasuryPage() {
    const [input, setInput] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const startAnalysis = async () => {
        if (!input) return;
        setIsAnalyzing(true);
        setResult(null);
        setError(null);

        try {
            // Determine if input is amount or ID
            const isAmount = !isNaN(Number(input));
            const payload = {
                proposal_id: isAmount ? "gov_action_manual" : input,
                amount: isAmount ? Number(input) * 1000000 : 50000000000, // Convert to lovelace or default
                proposer_id: "stake_test_123",
                metadata: {
                    title: "Manual Analysis",
                    abstract: "User initiated analysis",
                    rationale: "Checking for risk"
                }
            };

            const response = await fetch("http://localhost:8000/api/v1/treasury/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Analysis failed");
            }
            const data = await response.json();

            setResult({
                riskScore: data.risk_score,
                zScore: data.stats.z_score,
                nclViolation: data.findings.some((f: string) => f.includes("UNUSUALLY_LARGE_WITHDRAWAL")),
                contextualRisk: data.risk_score / 100,
                flags: data.findings,
                reasoning: `Risk Score: ${data.risk_score}. Verdict: ${data.vote}.`
            });

        } catch (error: any) {
            console.error(error);
            setError(error.message || "Analysis failed");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <ProtectedPage>
        <main className="min-h-screen text-ghost-white overflow-hidden relative selection:bg-amber-500/30 pt-24 pb-8 px-4 md:px-8">
            {/* Base Background */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,182,39,0.1)_0%,transparent_60%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />

            <div className="max-w-7xl mx-auto space-y-8 relative z-10">
                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.div
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs font-mono tracking-widest"
                    >
                        <Coins className="w-3 h-3" />
                        TREASURY GUARDIAN AGENT
                    </motion.div>
                    <h1 className="text-4xl md:text-6xl font-orbitron font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50">
                        <ScrambleText text="FISCAL INTEGRITY" />
                    </h1>
                    <p className="text-white/50 max-w-2xl mx-auto font-light">
                        AI-powered detection of treasury anomalies, net change limit violations, and contextual risk factors.
                    </p>
                </div>

                {/* Input Section */}
                <Card className="p-8 bg-black/40 border-amber-500/20 backdrop-blur-xl rounded-2xl max-w-3xl mx-auto relative z-20 shadow-[0_0_30px_rgba(255,182,39,0.05)]">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 relative group">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <Search className="w-5 h-5 text-amber-500/50 group-focus-within:text-amber-500 transition-colors" />
                            </div>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Enter Proposal ID or Amount (ADA)..."
                                className="w-full h-14 pl-12 pr-4 bg-black/50 border border-white/10 rounded-xl focus:outline-none focus:border-amber-500/50 text-white font-mono placeholder:text-white/20 transition-all relative z-50"
                            />
                        </div>
                        <Button
                            onClick={startAnalysis}
                            disabled={isAnalyzing || !input}
                            className="h-14 px-8 text-lg font-orbitron tracking-wider bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/50 text-amber-500"
                        >
                            {isAnalyzing ? "CALCULATING..." : "ANALYZE RISK"}
                        </Button>
                    </div>
                </Card>

                {/* Error Display */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className="max-w-3xl mx-auto p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-400 font-mono text-sm"
                        >
                            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Results Area */}
                <AnimatePresence mode="wait">
                    {result && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="grid grid-cols-1 md:grid-cols-12 gap-6"
                        >
                            {/* Left: Gauge */}
                            <div className="md:col-span-4">
                                <HolographicCard className="h-full p-8 bg-black/40 border-amber-500/20 flex items-center justify-center">
                                    <TreasuryRiskGauge riskScore={result.riskScore} />
                                </HolographicCard>
                            </div>

                            {/* Right: Details */}
                            <div className="md:col-span-8 space-y-6">
                                {/* Stats Grid */}
                                <div className="grid grid-cols-3 gap-4">
                                    <Card className="p-4 bg-white/5 border-white/10 text-center">
                                        <div className="text-xs text-white/40 font-mono uppercase mb-1">Z-Score</div>
                                        <div className={`text-2xl font-orbitron font-bold ${result.zScore > 3 ? "text-red-500" : "text-white"}`}>
                                            {result.zScore.toFixed(2)}
                                        </div>
                                    </Card>
                                    <Card className="p-4 bg-white/5 border-white/10 text-center">
                                        <div className="text-xs text-white/40 font-mono uppercase mb-1">NCL Check</div>
                                        <div className={`text-2xl font-orbitron font-bold ${result.nclViolation ? "text-red-500" : "text-green-400"}`}>
                                            {result.nclViolation ? "FAIL" : "PASS"}
                                        </div>
                                    </Card>
                                    <Card className="p-4 bg-white/5 border-white/10 text-center">
                                        <div className="text-xs text-white/40 font-mono uppercase mb-1">Context Risk</div>
                                        <div className="text-2xl font-orbitron font-bold text-amber-500">
                                            {result.contextualRisk.toFixed(2)}
                                        </div>
                                    </Card>
                                </div>

                                {/* Reasoning */}
                                <Card className="p-6 bg-amber-500/5 border-amber-500/20 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4 opacity-20">
                                        <ShieldAlert className="w-12 h-12 text-amber-500" />
                                    </div>
                                    <h3 className="text-amber-500 font-orbitron font-bold mb-2">ANALYSIS REASONING</h3>
                                    <p className="text-white/80 font-light leading-relaxed">
                                        {result.reasoning}
                                    </p>

                                    {result.flags.length > 0 && (
                                        <div className="mt-4 space-y-2">
                                            {result.flags.map((flag: string, i: number) => (
                                                <div key={i} className="flex items-center gap-2 text-xs font-mono text-red-400 bg-red-500/10 px-3 py-1 rounded border border-red-500/20">
                                                    <AlertTriangle className="w-3 h-3" />
                                                    {flag}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </Card>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
        </ProtectedPage>
    );
}
