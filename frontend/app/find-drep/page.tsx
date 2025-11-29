"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Users, TrendingUp, Scale, CheckCircle, Star, Target } from "lucide-react";

interface DRep {
    drep_id: string;
    name: string;
    alignment_score: number;
    voting_style: string;
    voting_record: {
        total_votes: number;
        yes_rate: number;
    };
    description: string;
    recommended: boolean;
}

interface RecommendationResponse {
    success: boolean;
    recommendations: DRep[];
    preference: string;
    total_dreps: number;
    timestamp: number;
}

export default function FindDRepPage() {
    const [preference, setPreference] = useState<"progressive" | "balanced" | "conservative">("balanced");
    const [recommendations, setRecommendations] = useState<DRep[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchRecommendations = async (selectedPreference: string) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/governance/dreps/recommend?preference=${selectedPreference}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: RecommendationResponse = await response.json();
            if (data.success) {
                setRecommendations(data.recommendations);
            } else {
                throw new Error("Failed to fetch recommendations");
            }
        } catch (err) {
            console.error("Error fetching recommendations:", err);
            setError(err instanceof Error ? err.message : "Unknown error occurred");
            setRecommendations([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePreferenceChange = (newPreference: "progressive" | "balanced" | "conservative") => {
        setPreference(newPreference);
        fetchRecommendations(newPreference);
    };

    // Initial load
    useEffect(() => {
        fetchRecommendations(preference);
    }, []);

    const getPreferenceDescription = (pref: string) => {
        switch (pref) {
            case "progressive":
                return "Prioritize innovation and ecosystem growth (70%+ yes votes)";
            case "balanced":
                return "Balanced approach to governance (40-70% yes votes)";
            case "conservative":
                return "Focus on stability and caution (30%- yes votes)";
            default:
                return "";
        }
    };

    const getVotingStyleColor = (style: string) => {
        switch (style) {
            case "Progressive":
                return "text-electric-cyan";
            case "Balanced":
                return "text-neon-orchid";
            case "Conservative":
                return "text-plasma-pink";
            default:
                return "text-white/60";
        }
    };

    const getAlignmentScoreColor = (score: number) => {
        if (score >= 80) return "text-green-400";
        if (score >= 60) return "text-amber-400";
        return "text-red-400";
    };

    return (
        <main className="min-h-screen text-ghost-white overflow-hidden relative selection:bg-neon-orchid/30 pt-24 pb-8 px-4 md:px-8">
            {/* Base Background Color */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />

            {/* Background Effects */}
            <div className="fixed inset-0 bg-[linear-gradient(rgba(0,245,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] -z-10" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,245,255,0.1)_0%,transparent_50%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />
            <div className="fixed inset-0 bg-[url('/protocol-circuit.png')] bg-cover bg-center opacity-[0.05] mix-blend-screen pointer-events-none -z-5" />

            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-electric-cyan/10 border border-electric-cyan/20 text-electric-cyan text-xs font-mono tracking-widest uppercase mb-4"
                    >
                        <Users className="w-3 h-3" />
                        DRep Recommendation Engine
                    </motion.div>
                    <h1 className="text-4xl md:text-6xl font-orbitron font-black tracking-tighter">
                        <ScrambleText text="FIND YOUR" /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-electric-cyan to-neon-orchid">DREP</span>
                    </h1>
                    <p className="text-white/60 max-w-2xl mx-auto text-lg">
                        Discover Delegate Representatives that align with your governance philosophy and voting preferences.
                    </p>
                </div>

                {/* Preference Selector */}
                <HolographicCard className="p-8 bg-black/40 border-white/10 backdrop-blur-xl rounded-2xl max-w-4xl mx-auto">
                    <div className="text-center mb-6">
                        <h2 className="text-2xl font-orbitron font-bold mb-2">Select Your Governance Style</h2>
                        <p className="text-white/60">{getPreferenceDescription(preference)}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {[
                            { key: "progressive" as const, label: "Progressive", icon: TrendingUp, desc: "Innovation First" },
                            { key: "balanced" as const, label: "Balanced", icon: Scale, desc: "Pragmatic Approach" },
                            { key: "conservative" as const, label: "Conservative", icon: Target, desc: "Stability Focus" }
                        ].map((option) => (
                            <motion.button
                                key={option.key}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => handlePreferenceChange(option.key)}
                                className={`p-6 rounded-xl border transition-all duration-200 ${
                                    preference === option.key
                                        ? "bg-electric-cyan/10 border-electric-cyan/50 text-electric-cyan"
                                        : "bg-black/30 border-white/10 text-white/60 hover:border-white/20 hover:text-white"
                                }`}
                            >
                                <div className="flex flex-col items-center gap-3">
                                    <option.icon className="w-8 h-8" />
                                    <div>
                                        <div className="font-orbitron font-bold text-lg">{option.label}</div>
                                        <div className="text-sm opacity-70">{option.desc}</div>
                                    </div>
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </HolographicCard>

                {/* Loading State */}
                <AnimatePresence>
                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="text-center py-12"
                        >
                            <div className="inline-flex items-center gap-4 px-6 py-3 rounded-full bg-black/40 border border-white/10 backdrop-blur-sm">
                                <div className="flex gap-2">
                                    <span className="w-2 h-2 rounded-full bg-electric-cyan animate-pulse" />
                                    <span className="w-2 h-2 rounded-full bg-electric-cyan animate-pulse delay-75" />
                                    <span className="w-2 h-2 rounded-full bg-electric-cyan animate-pulse delay-150" />
                                </div>
                                <span className="font-mono text-white/80">Analyzing DRep alignment...</span>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Error State */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="text-center py-8"
                        >
                            <Card className="bg-red-500/10 border-red-500/20 text-red-400 p-6 max-w-2xl mx-auto">
                                <div className="flex items-center gap-3 justify-center mb-2">
                                    <Target className="w-5 h-5" />
                                    <span className="font-orbitron font-bold">Connection Error</span>
                                </div>
                                <p className="text-sm">{error}</p>
                                <Button
                                    onClick={() => fetchRecommendations(preference)}
                                    className="mt-4 bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-400"
                                >
                                    Retry
                                </Button>
                            </Card>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Recommendations Grid */}
                <AnimatePresence>
                    {!isLoading && !error && recommendations.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        >
                            {recommendations.map((drep, index) => (
                                <motion.div
                                    key={drep.drep_id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <HolographicCard className={`p-6 bg-black/40 border-white/10 backdrop-blur-xl rounded-2xl h-full hover:border-electric-cyan/30 transition-all duration-300 ${
                                        drep.recommended ? "ring-1 ring-electric-cyan/20" : ""
                                    }`}>
                                        <div className="flex flex-col h-full">
                                            {/* Header */}
                                            <div className="flex items-start justify-between mb-4">
                                                <div className="flex-1">
                                                    <h3 className="font-orbitron font-bold text-lg text-white mb-1">
                                                        {drep.name}
                                                    </h3>
                                                    <p className="text-white/60 text-sm leading-relaxed">
                                                        {drep.description}
                                                    </p>
                                                </div>
                                                {drep.recommended && (
                                                    <CheckCircle className="w-6 h-6 text-electric-cyan flex-shrink-0 ml-2" />
                                                )}
                                            </div>

                                            {/* Alignment Score */}
                                            <div className="mb-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-sm font-mono text-white/60">Alignment Score</span>
                                                    <span className={`font-mono font-bold text-lg ${getAlignmentScoreColor(drep.alignment_score)}`}>
                                                        {drep.alignment_score.toFixed(1)}%
                                                    </span>
                                                </div>
                                                <div className="w-full bg-white/10 rounded-full h-2">
                                                    <div
                                                        className="bg-gradient-to-r from-electric-cyan to-neon-orchid h-2 rounded-full transition-all duration-500"
                                                        style={{ width: `${drep.alignment_score}%` }}
                                                    />
                                                </div>
                                            </div>

                                            {/* Voting Style */}
                                            <div className="mb-4">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Star className="w-4 h-4 text-yellow-400" />
                                                    <span className="text-sm font-mono text-white/60">Voting Style</span>
                                                </div>
                                                <span className={`font-orbitron font-bold ${getVotingStyleColor(drep.voting_style)}`}>
                                                    {drep.voting_style}
                                                </span>
                                            </div>

                                            {/* Voting Record */}
                                            <div className="mb-4">
                                                <div className="text-sm font-mono text-white/60 mb-2">Voting Record</div>
                                                <div className="grid grid-cols-2 gap-4 text-center">
                                                    <div>
                                                        <div className="font-mono font-bold text-white text-lg">
                                                            {drep.voting_record.total_votes}
                                                        </div>
                                                        <div className="text-xs text-white/40 uppercase">Total Votes</div>
                                                    </div>
                                                    <div>
                                                        <div className="font-mono font-bold text-electric-cyan text-lg">
                                                            {drep.voting_record.yes_rate.toFixed(1)}%
                                                        </div>
                                                        <div className="text-xs text-white/40 uppercase">Yes Rate</div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Recommended Badge */}
                                            {drep.recommended && (
                                                <div className="mt-auto">
                                                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-electric-cyan/10 border border-electric-cyan/20 text-electric-cyan text-xs font-mono">
                                                        <Star className="w-3 h-3" />
                                                        RECOMMENDED
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </HolographicCard>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Empty State */}
                <AnimatePresence>
                    {!isLoading && !error && recommendations.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="text-center py-12"
                        >
                            <Card className="bg-black/40 border-white/10 text-white/60 p-8 max-w-md mx-auto">
                                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                <h3 className="font-orbitron font-bold text-lg mb-2">No DReps Found</h3>
                                <p className="text-sm">Unable to load Delegate Representatives. Please try again.</p>
                            </Card>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
    );
}
