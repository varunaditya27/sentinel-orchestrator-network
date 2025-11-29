import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "./ui/Card";

interface LogEntry {
    id: string;
    agent: "SENTINEL" | "ORACLE" | "MIDNIGHT";
    message: string;
    type: "info" | "warning" | "error" | "success" | "action";
    timestamp: number;
    details?: string[];
}

interface MatrixTerminalProps {
    logs: LogEntry[];
    isActive: boolean;
}

export const MatrixTerminal: React.FC<MatrixTerminalProps> = ({ logs, isActive }) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    if (!isActive) return null;

    return (
        <Card className="w-full h-[400px] bg-black border-neon-orchid/30 font-mono text-sm overflow-hidden flex flex-col relative shadow-[0_0_40px_rgba(0,0,0,0.5)] group">
            {/* CRT Effects */}
            <div className="absolute inset-0 pointer-events-none z-20 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />
            <div className="absolute inset-0 pointer-events-none z-20 animate-pulse opacity-5 bg-white mix-blend-overlay" />

            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-white/10 bg-white/5 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]" />
                    <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                </div>
                <div className="text-neon-orchid text-xs tracking-widest font-bold animate-pulse">SENTINEL ORCHESTRATOR NETWORK v2.0</div>
            </div>

            {/* Terminal Body */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth relative z-10">
                <AnimatePresence>
                    {logs.map((log) => (
                        <motion.div
                            key={log.id}
                            initial={{ opacity: 0, x: -20, filter: "blur(4px)" }}
                            animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                            transition={{ duration: 0.3, type: "spring" }}
                            className="flex flex-col gap-1 font-jetbrains-mono"
                        >
                            <div className="flex items-baseline gap-3">
                                <span className="text-xs text-white/30 select-none">
                                    {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                </span>
                                <span
                                    className={
                                        log.agent === "SENTINEL" ? "text-neon-orchid font-bold drop-shadow-[0_0_5px_rgba(255,0,110,0.8)]" :
                                            log.agent === "ORACLE" ? "text-electric-cyan font-bold drop-shadow-[0_0_5px_rgba(0,245,255,0.8)]" :
                                                "text-amber-warning font-bold drop-shadow-[0_0_5px_rgba(255,182,39,0.8)]"
                                    }
                                >
                                    [{log.agent}]
                                </span>
                                <span className={
                                    log.type === "error" ? "text-red-500 font-bold" :
                                        log.type === "warning" ? "text-amber-warning" :
                                            log.type === "success" ? "text-green-400" :
                                                log.type === "action" ? "text-plasma-pink italic" :
                                                    "text-ghost-white"
                                }>
                                    {log.message}
                                </span>
                            </div>
                            {log.details && (
                                <div className="pl-24 space-y-1 border-l border-white/10 ml-4">
                                    {log.details.map((detail, idx) => (
                                        <div key={idx} className="text-white/50 text-xs flex items-center gap-2">
                                            <span className="w-1 h-1 bg-white/20 rounded-full" />
                                            {detail}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Typing Cursor */}
                <motion.div
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="w-2 h-4 bg-neon-orchid ml-2 inline-block shadow-[0_0_8px_#FF006E]"
                />
            </div>
        </Card>
    );
};
