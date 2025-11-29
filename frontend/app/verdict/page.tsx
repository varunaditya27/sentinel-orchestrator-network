"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, ArrowLeft, Lock, FileText, Share2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ThreatProofCard } from "@/components/ThreatProofCard";

function VerdictContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const status = (searchParams.get("status") as "SAFE" | "DANGER" | "WARNING") || "DANGER";
    const [showProof, setShowProof] = useState(false);

    // Sound effect simulation (visual only for now)
    useEffect(() => {
        // In a real app, play sound here
    }, [status]);

    const isDanger = status === "DANGER";
    const isWarning = status === "WARNING";

    return (
        <main className="min-h-screen bg-obsidian-core text-ghost-white overflow-hidden relative selection:bg-neon-orchid/30 flex flex-col pt-32">
            {/* Background Effects */}
            <div className={`fixed inset-0 transition-colors duration-1000 ${isDanger ? "bg-red-950/20" : isWarning ? "bg-amber-950/20" : "bg-electric-cyan/10"
                }`} />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,transparent_0%,#000_100%)]" />

            {/* Content Container */}
            <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-4 md:p-8">

                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.5, type: "spring" }}
                    className="w-full max-w-5xl"
                >
                    {/* Verdict Header */}
                    <div className="text-center mb-12 relative">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                            className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center mb-8 border-4 shadow-[0_0_50px_rgba(0,0,0,0.5)] ${isDanger ? "bg-red-500/10 border-red-500 shadow-red-500/50" :
                                isWarning ? "bg-amber-500/10 border-amber-500 shadow-amber-500/50" :
                                    "bg-electric-cyan/10 border-electric-cyan shadow-electric-cyan/50"
                                }`}
                        >
                            <motion.div
                                animate={{ scale: [1, 1.1, 1] }}
                                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                            >
                                {isDanger ? (
                                    <AlertTriangle className="w-16 h-16 text-red-500" />
                                ) : isWarning ? (
                                    <AlertTriangle className="w-16 h-16 text-amber-500" />
                                ) : (
                                    <CheckCircle className="w-16 h-16 text-electric-cyan" />
                                )}
                            </motion.div>
                        </motion.div>

                        <motion.h1
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className={`text-6xl md:text-8xl font-orbitron font-black tracking-tighter mb-4 drop-shadow-[0_0_20px_rgba(0,0,0,0.8)] ${isDanger ? "text-red-500 shadow-red-500/50" :
                                isWarning ? "text-amber-500 shadow-amber-500/50" :
                                    "text-electric-cyan shadow-electric-cyan/50"
                                }`}
                        >
                            {isDanger ? "THREAT DETECTED" : isWarning ? "POTENTIAL RISK" : "TRANSACTION SAFE"}
                        </motion.h1>

                        <motion.p
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-xl md:text-2xl text-white/70 max-w-2xl mx-auto font-light"
                        >
                            {isDanger
                                ? "Sentinel has intercepted a malicious interaction on a minority fork. Your assets are at risk."
                                : isWarning
                                    ? "Minor anomalies detected in block propagation. Proceed with extreme caution."
                                    : "Consensus verified across 50+ nodes. No anomalies detected."}
                        </motion.p>
                    </div>

                    {/* Action Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                        {/* Proof Card */}
                        <motion.div
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.6 }}
                        >
                            <Card className="h-full p-8 bg-black/40 border-white/10 backdrop-blur-xl hover:bg-white/5 transition-colors group cursor-pointer" onClick={() => setShowProof(true)}>
                                <div className="flex items-start justify-between mb-6">
                                    <div className={`p-3 rounded-lg ${isDanger ? "bg-red-500/20 text-red-500" :
                                        isWarning ? "bg-amber-500/20 text-amber-500" :
                                            "bg-electric-cyan/20 text-electric-cyan"
                                        }`}>
                                        <Lock className="w-6 h-6" />
                                    </div>
                                    <ArrowRightIcon className="w-5 h-5 text-white/30 group-hover:text-white group-hover:translate-x-1 transition-all" />
                                </div>
                                <h3 className="text-2xl font-orbitron font-bold mb-2">View Cryptographic Proof</h3>
                                <p className="text-white/50">Examine the ZK-Proof generated by Midnight agents verifying the chain split.</p>
                            </Card>
                        </motion.div>

                        {/* Report Card */}
                        <motion.div
                            initial={{ x: 20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.7 }}
                        >
                            <Card className="h-full p-8 bg-black/40 border-white/10 backdrop-blur-xl hover:bg-white/5 transition-colors group cursor-pointer">
                                <div className="flex items-start justify-between mb-6">
                                    <div className={`p-3 rounded-lg ${isDanger ? "bg-red-500/20 text-red-500" :
                                        isWarning ? "bg-amber-500/20 text-amber-500" :
                                            "bg-electric-cyan/20 text-electric-cyan"
                                        }`}>
                                        <FileText className="w-6 h-6" />
                                    </div>
                                    <ArrowRightIcon className="w-5 h-5 text-white/30 group-hover:text-white group-hover:translate-x-1 transition-all" />
                                </div>
                                <h3 className="text-2xl font-orbitron font-bold mb-2">Download Audit Report</h3>
                                <p className="text-white/50">Get a detailed PDF report of the scan analysis and node responses.</p>
                            </Card>
                        </motion.div>
                    </div>

                    {/* Footer Actions */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.8 }}
                        className="flex justify-center gap-4 mt-12"
                    >
                        <Button variant="secondary" onClick={() => router.push("/dashboard")} className="gap-2">
                            <ArrowLeft className="w-4 h-4" />
                            New Scan
                        </Button>
                        <Button variant="primary" className="gap-2">
                            <Share2 className="w-4 h-4" />
                            Share Verdict
                        </Button>
                    </motion.div>

                </motion.div>
            </div>

            {/* Proof Overlay */}
            <AnimatePresence>
                {showProof && (
                    <ThreatProofCard
                        verdict={status}
                        onClose={() => setShowProof(false)}
                    />
                )}
            </AnimatePresence>
        </main>
    );
}

export default function VerdictPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-obsidian-core flex items-center justify-center text-white">Loading Verdict...</div>}>
            <VerdictContent />
        </Suspense>
    );
}

function ArrowRightIcon({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="M5 12h14" />
            <path d="m12 5 7 7-7 7" />
        </svg>
    );
}
