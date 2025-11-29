"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { MatrixTerminal, LogEntry } from "@/components/MatrixTerminal";
import { HolographicCard } from "@/components/HolographicCard";
import { ScrambleText } from "@/components/ScrambleText";
import { Shield, FileText, Clock, TrendingUp, AlertTriangle, CheckCircle, XCircle, RefreshCw, Vote } from "lucide-react";

// Types
interface Proposal {
    id: string;
    title: string;
    amount: number; // ADA
    status: string;
    ends_in: string; // human readable time
}

interface AgentStatus {
    name: string;
    status: "idle" | "running" | "completed" | "error";
    time: string;
    result?: string;
    flags?: string[];
    support?: number;
    risk_score?: number;
    ncl_status?: string;
}

interface Verdict {
    recommendation: "YES" | "NO" | "ABSTAIN";
    confidence: number;
    violations: string[];
    sentiment: string;
    summary: string;
}

export default function GovernancePage() {
    const [proposals, setProposals] = useState<Proposal[]>([]);
    const [analyzing, setAnalyzing] = useState(false);
    const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
    const [verdict, setVerdict] = useState<Verdict | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [taskId, setTaskId] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    const agents: AgentStatus[] = [
        { name: "ProposalFetcher", status: "idle", time: "--:--", result: "" },
        { name: "PolicyAnalyzer", status: "idle", time: "--:--", result: "", flags: [] },
        { name: "SentimentAnalyzer", status: "idle", time: "--:--", result: "", support: 0 },
        { name: "TreasuryGuardian", status: "idle", time: "--:--", result: "", risk_score: 0, ncl_status: "" }
    ];

    const [agentStatuses, setAgentStatuses] = useState(agents);

    useEffect(() => {
        fetchProposals();
    }, []);

    const fetchProposals = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/v1/governance/proposals");
            if (res.ok) {
                const data = await res.json();
                setProposals(data);
            }
        } catch (error) {
            console.error("Failed to fetch proposals:", error);
        }
    };

    const startAnalysis = async (proposal: Proposal) => {
        if (analyzing) return;

        setSelectedProposal(proposal);
        setAnalyzing(true);
        setVerdict(null);
        setLogs([]);
        setAgentStatuses(agents.map(a => ({ ...a, status: "idle" })));

        try {
            const response = await fetch("http://localhost:8000/api/v1/governance/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ proposal_id: proposal.id })
            });

            const data = await response.json();
            setTaskId(data.task_id);

            // Connect WebSocket
            const ws = new WebSocket(`ws://localhost:8000/ws/governance/${data.task_id}`);
            wsRef.current = ws;

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                setAnalyzing(false);
            };

            ws.onclose = () => {
                setAnalyzing(false);
            };

        } catch (error) {
            console.error("Analysis failed:", error);
            setAnalyzing(false);
        }
    };

    const handleWebSocketMessage = (message: any) => {
        if (message.type === "log") {
            setLogs(prev => [...prev, {
                id: Math.random().toString(),
                agent: message.agent,
                message: message.content,
                type: message.level || "info",
                timestamp: Date.now()
            }]);
        } else if (message.type === "agent_update") {
            setAgentStatuses(prev => prev.map(agent =>
                agent.name === message.agent_name
                    ? { ...agent, ...message.update }
                    : agent
            ));
        } else if (message.type === "verdict") {
            setVerdict(message.verdict);
            setAnalyzing(false);
            if (wsRef.current) {
                wsRef.current.close();
            }
        }
    };

    const renderProposalRow = (proposal: Proposal) => (
        <motion.div
            key={proposal.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between p-4 bg-black/20 border border-white/10 rounded-lg hover:bg-black/30 transition-colors"
        >
            <div className="flex items-center gap-4">
                <div className="text-neon-orchid font-mono text-sm">{proposal.id}</div>
                <div className="flex-1">
                    <div className="font-medium text-ghost-white">{proposal.title}</div>
                    <div className="text-xs text-white/50 flex items-center gap-4">
                        <span className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" />
                            {proposal.amount} ADA
                        </span>
                        <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {proposal.ends_in}
                        </span>
                    </div>
                </div>
            </div>
            <div className="flex items-center gap-3">
                <span className={`px-2 py-1 text-xs rounded-full ${
                    proposal.status === "active" ? "bg-electric-cyan/20 text-electric-cyan" :
                    proposal.status === "ended" ? "bg-amber-warning/20 text-amber-warning" :
                    "bg-white/10 text-white/50"
                }`}>
                    {proposal.status}
                </span>
                <Button
                    onClick={() => startAnalysis(proposal)}
                    disabled={analyzing}
                    className="px-4 py-2 text-sm"
                >
                    ANALYZE
                </Button>
            </div>
        </motion.div>
    );

    const renderAgentCard = (agent: AgentStatus) => (
        <HolographicCard key={agent.name} className="p-4 bg-black/40 border-white/10">
            <div className="flex items-center justify-between mb-2">
                <h3 className="font-orbitron text-sm font-bold text-neon-orchid">{agent.name}</h3>
                <div className={`w-2 h-2 rounded-full ${
                    agent.status === "running" ? "bg-amber-warning animate-pulse" :
                    agent.status === "completed" ? "bg-electric-cyan" :
                    agent.status === "error" ? "bg-neon-orchid" :
                    "bg-white/20"
                }`} />
            </div>
            <div className="text-xs text-white/50 mb-2">{agent.time}</div>
            {agent.result && (
                <div className="text-xs text-ghost-white mb-2">{agent.result}</div>
            )}
            {agent.flags && agent.flags.length > 0 && (
                <div className="text-xs text-amber-warning">
                    Flags: {agent.flags.join(", ")}
                </div>
            )}
            {agent.support !== undefined && (
                <div className="text-xs text-electric-cyan">
                    Support: {agent.support}%
                </div>
            )}
            {agent.risk_score !== undefined && (
                <div className="text-xs text-plasma-pink">
                    Risk: {agent.risk_score}/100
                </div>
            )}
            {agent.ncl_status && (
                <div className="text-xs text-green-400">
                    NCL: {agent.ncl_status}
                </div>
            )}
        </HolographicCard>
    );

    return (
        <main className="min-h-screen text-ghost-white overflow-hidden relative pt-24 pb-8 px-4 md:px-8">
            {/* Base Background */}
            <div className="fixed inset-0 bg-obsidian-core -z-50" />
            <div className="fixed inset-0 bg-[linear-gradient(rgba(0,245,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,245,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] -z-10" />
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,0,0,0)_0%,rgba(0,0,0,0.8)_100%)] -z-10" />
            <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-0" />

            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                >
                    <h1 className="font-orbitron font-bold text-4xl tracking-wider">
                        <ScrambleText text="GOVERNANCE PROPOSAL ANALYZER" />
                    </h1>
                    <p className="text-white/50 mt-2">AI-Powered Proposal Analysis for Cardano Governance</p>
                </motion.div>

                {/* Proposals List */}
                <HolographicCard className="p-6 bg-black/40 border-white/10">
                    <div className="flex items-center gap-3 mb-6">
                        <FileText className="w-6 h-6 text-neon-orchid" />
                        <h2 className="font-orbitron font-bold text-xl">Active Proposals</h2>
                    </div>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                        {proposals.length === 0 ? (
                            <div className="text-center text-white/50 py-8">
                                <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
                                Loading proposals...
                            </div>
                        ) : (
                            proposals.map(renderProposalRow)
                        )}
                    </div>
                </HolographicCard>

                {/* Analysis Panel */}
                <AnimatePresence>
                    {analyzing && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-6"
                        >
                            <HolographicCard className="p-6 bg-black/40 border-white/10">
                                <div className="flex items-center gap-3 mb-6">
                                    <Shield className="w-6 h-6 text-electric-cyan" />
                                    <h2 className="font-orbitron font-bold text-xl">Live Analysis</h2>
                                    <div className="ml-auto flex items-center gap-2">
                                        <RefreshCw className="w-4 h-4 animate-spin text-amber-warning" />
                                        <span className="text-sm text-amber-warning">Analyzing...</span>
                                    </div>
                                </div>

                                {/* Agent Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                                    {agentStatuses.map(renderAgentCard)}
                                </div>

                                {/* Terminal */}
                                <MatrixTerminal logs={logs} isActive={true} />
                            </HolographicCard>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Verdict Display */}
                <AnimatePresence>
                    {verdict && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                        >
                            <HolographicCard className="p-6 bg-black/40 border-white/10">
                                <div className="text-center mb-6">
                                    <h2 className="font-orbitron font-bold text-2xl mb-2">Final Verdict</h2>
                                    <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full text-lg font-bold ${
                                        verdict.recommendation === "YES" ? "bg-electric-cyan/20 text-electric-cyan" :
                                        verdict.recommendation === "NO" ? "bg-neon-orchid/20 text-neon-orchid" :
                                        "bg-amber-warning/20 text-amber-warning"
                                    }`}>
                                        {verdict.recommendation === "YES" && <CheckCircle className="w-5 h-5" />}
                                        {verdict.recommendation === "NO" && <XCircle className="w-5 h-5" />}
                                        {verdict.recommendation === "ABSTAIN" && <AlertTriangle className="w-5 h-5" />}
                                        {verdict.recommendation}
                                    </div>
                                    <div className="text-sm text-white/50 mt-2">
                                        Confidence: {verdict.confidence}%
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                    <div>
                                        <h3 className="font-orbitron font-bold mb-3 flex items-center gap-2">
                                            <AlertTriangle className="w-4 h-4 text-amber-warning" />
                                            Violations & Flags
                                        </h3>
                                        {verdict.violations.length > 0 ? (
                                            <ul className="space-y-2">
                                                {verdict.violations.map((violation, idx) => (
                                                    <li key={idx} className="text-sm text-amber-warning flex items-start gap-2">
                                                        <span className="w-1 h-1 bg-amber-warning rounded-full mt-2 flex-shrink-0" />
                                                        {violation}
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <div className="text-sm text-green-400">No violations detected</div>
                                        )}
                                    </div>

                                    <div>
                                        <h3 className="font-orbitron font-bold mb-3 flex items-center gap-2">
                                            <TrendingUp className="w-4 h-4 text-plasma-pink" />
                                            Community Sentiment
                                        </h3>
                                        <div className="text-sm text-plasma-pink">{verdict.sentiment}</div>
                                        <div className="text-xs text-white/50 mt-2">{verdict.summary}</div>
                                    </div>
                                </div>

                                <div className="flex justify-center gap-4">
                                    <Button className="px-6 py-3 bg-electric-cyan/20 hover:bg-electric-cyan/30 text-electric-cyan border-electric-cyan/50">
                                        <Vote className="w-4 h-4 mr-2" />
                                        VOTE YES
                                    </Button>
                                    <Button className="px-6 py-3 bg-neon-orchid/20 hover:bg-neon-orchid/30 text-neon-orchid border-neon-orchid/50">
                                        <Vote className="w-4 h-4 mr-2" />
                                        VOTE NO
                                    </Button>
                                    <Button className="px-6 py-3 bg-amber-warning/20 hover:bg-amber-warning/30 text-amber-warning border-amber-warning/50">
                                        <Vote className="w-4 h-4 mr-2" />
                                        ABSTAIN
                                    </Button>
                                    <Button variant="secondary" className="px-6 py-3">
                                        MANUAL REVIEW
                                    </Button>
                                </div>
                            </HolographicCard>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
    );
}
