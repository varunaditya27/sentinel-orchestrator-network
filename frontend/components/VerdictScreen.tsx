import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, ShieldAlert, FileText, RefreshCw, AlertTriangle } from "lucide-react";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

interface VerdictScreenProps {
    status: "SAFE" | "DANGER";
    onReset: () => void;
    onViewProof: () => void;
}

export const VerdictScreen: React.FC<VerdictScreenProps> = ({ status, onReset, onViewProof }) => {
    const isSafe = status === "SAFE";

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-core/95 backdrop-blur-xl p-4"
        >
            {/* Dynamic Background */}
            <div className={`absolute inset-0 opacity-20 ${isSafe ? "bg-electric-cyan" : "bg-red-600"} mix-blend-overlay animate-pulse`} />

            {/* Shattered Glass Effect for Danger */}
            {!isSafe && (
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
                </div>
            )}

            <Card className={`w-full max-w-3xl border-2 ${isSafe ? "border-electric-cyan shadow-[0_0_100px_rgba(0,245,255,0.2)]" : "border-red-500 shadow-[0_0_100px_rgba(220,38,38,0.3)]"} relative overflow-hidden transform transition-all duration-500`}>
                <div className="relative z-10 flex flex-col items-center text-center space-y-8 py-12 px-8">

                    {/* Icon Animation */}
                    <motion.div
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{ type: "spring", stiffness: 100, damping: 10, delay: 0.2 }}
                        className={`p-8 rounded-full ${isSafe ? "bg-electric-cyan/10 border border-electric-cyan" : "bg-red-500/10 border border-red-500"}`}
                    >
                        {isSafe ? (
                            <ShieldCheck className="w-32 h-32 text-electric-cyan drop-shadow-[0_0_20px_rgba(0,245,255,0.8)]" />
                        ) : (
                            <ShieldAlert className="w-32 h-32 text-red-500 drop-shadow-[0_0_20px_rgba(220,38,38,0.8)] animate-pulse" />
                        )}
                    </motion.div>

                    <div className="space-y-4">
                        <motion.h2
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className={`text-5xl md:text-6xl font-orbitron font-black tracking-tighter ${isSafe ? "text-electric-cyan" : "text-red-500"}`}
                        >
                            {isSafe ? "TRANSACTION VERIFIED" : "GOVERNANCE SPLIT DETECTED"}
                        </motion.h2>
                        <motion.p
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-ghost-white/80 text-xl max-w-xl mx-auto font-light"
                        >
                            {isSafe
                                ? "Canonical chain confirmed. Protocol V3 compliant. Safe to sign."
                                : "Your node is on a ghost chain. Threat type: Replay Attack Vector."}
                        </motion.p>
                    </div>

                    {/* Stats Grid */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-lg"
                    >
                        <div className="bg-void-gray/50 p-6 rounded-xl border border-white/5 backdrop-blur-sm">
                            <div className="text-xs text-white/40 uppercase tracking-wider mb-2 font-mono">Consensus Status</div>
                            <div className={`font-orbitron text-2xl font-bold ${isSafe ? "text-green-400" : "text-red-400"}`}>
                                {isSafe ? "Mainnet (99.2%)" : "Minority Fork (30%)"}
                            </div>
                        </div>
                        <div className="bg-void-gray/50 p-6 rounded-xl border border-white/5 backdrop-blur-sm">
                            <div className="text-xs text-white/40 uppercase tracking-wider mb-2 font-mono">Risk Assessment</div>
                            <div className={`font-orbitron text-2xl font-bold ${isSafe ? "text-green-400" : "text-red-500"}`}>
                                {isSafe ? "LOW RISK" : "CRITICAL"}
                            </div>
                        </div>
                    </motion.div>

                    {/* Actions */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.8 }}
                        className="flex gap-6 pt-6"
                    >
                        <Button variant={isSafe ? "primary" : "secondary"} onClick={onViewProof} className="min-w-[160px]">
                            <FileText className="w-4 h-4 mr-2" />
                            View Proof
                        </Button>
                        <Button variant={isSafe ? "secondary" : "primary"} onClick={onReset} className="min-w-[160px]">
                            {isSafe ? <RefreshCw className="w-4 h-4 mr-2" /> : <AlertTriangle className="w-4 h-4 mr-2" />}
                            {isSafe ? "New Scan" : "Switch Node"}
                        </Button>
                    </motion.div>
                </div>
            </Card>
        </motion.div>
    );
};
