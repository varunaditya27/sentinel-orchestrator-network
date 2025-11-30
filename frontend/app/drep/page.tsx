"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { DRepConsensus } from "@/components/DRepConsensus";
import { Users, Vote, Activity, Search } from "lucide-react";
import { ProtectedPage } from "@/components/ProtectedPage";

export default function DRepPage() {
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
            const response = await fetch("http://localhost:8000/api/v1/drep/consensus", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ proposal_id: input })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Analysis failed");
            }
            const data = await response.json();

            setResult({
                finalVerdict: data.finalVerdict,
                votes: data.votes
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
        <main className="min-h-screen text-ghost-white overflow-hidden relative selection:bg-electric-cyan/30 pt-24 pb-8 px-4 md:px-8">
            {/* Base Background */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(0,245,255,0.1)_0%,transparent_60%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />

            <div className="max-w-7xl mx-auto space-y-8 relative z-10">
                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.div
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-electric-cyan/10 border border-electric-cyan/20 text-electric-cyan text-xs font-mono tracking-widest"
                    >
                        <Vote className="w-3 h-3" />
                        DREP HELPER AGENT
                    </motion.div>
                    <h1 className="text-4xl md:text-6xl font-orbitron font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50">
                        <ScrambleText text="CONSENSUS ENGINE" />
                    </h1>
                    <p className="text-white/50 max-w-2xl mx-auto font-light">
                        Aggregated governance intelligence from Policy, Sentiment, and Treasury agents.
                    </p>
                </div>

                {/* Input Section */}
                <Card className="p-8 bg-black/40 border-electric-cyan/20 backdrop-blur-xl rounded-2xl max-w-3xl mx-auto relative z-20 shadow-[0_0_30px_rgba(0,245,255,0.05)]">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 relative group">
                            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                                <Search className="w-5 h-5 text-electric-cyan/50 group-focus-within:text-electric-cyan transition-colors" />
                            </div>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Enter Governance Action ID..."
                                className="w-full h-14 pl-12 pr-4 bg-black/50 border border-white/10 rounded-xl focus:outline-none focus:border-electric-cyan/50 text-white font-mono placeholder:text-white/20 transition-all relative z-50"
                            />
                        </div>
                        <Button
                            onClick={startAnalysis}
                            disabled={isAnalyzing || !input}
                            className="h-14 px-8 text-lg font-orbitron tracking-wider bg-electric-cyan/10 hover:bg-electric-cyan/20 border-electric-cyan/50 text-electric-cyan"
                        >
                            {isAnalyzing ? "AGGREGATING..." : "GET VERDICT"}
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
                            <Activity className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Results Area */}
                <AnimatePresence mode="wait">
                    {result && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="max-w-4xl mx-auto"
                        >
                            <HolographicCard className="p-8 bg-black/40 border-white/10">
                                <DRepConsensus votes={result.votes} finalVerdict={result.finalVerdict} />
                            </HolographicCard>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
        </ProtectedPage>
    );
}
