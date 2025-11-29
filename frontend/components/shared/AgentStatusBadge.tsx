"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle, AlertTriangle, Zap } from "lucide-react";

interface AgentStatusBadgeProps {
    agentsActive?: number;
    totalAgents?: number;
    errorAgent?: string;
    className?: string;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({
    agentsActive = 4,
    totalAgents = 4,
    errorAgent,
    className = ""
}) => {
    const isAllActive = agentsActive === totalAgents && !errorAgent;
    const hasError = !!errorAgent;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono tracking-wide ${
                hasError
                    ? "bg-neon-orchid/10 border border-neon-orchid/30 text-neon-orchid"
                    : isAllActive
                        ? "bg-electric-cyan/10 border border-electric-cyan/30 text-electric-cyan"
                        : "bg-amber-warning/10 border border-amber-warning/30 text-amber-warning"
            } ${className}`}
        >
            {hasError ? (
                <>
                    <AlertTriangle className="w-3 h-3" />
                    <span>Agent Error: {errorAgent}</span>
                </>
            ) : (
                <>
                    <CheckCircle className="w-3 h-3" />
                    <span>Agents Active: {agentsActive}/{totalAgents}</span>
                    <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Zap className="w-3 h-3" />
                    </motion.div>
                </>
            )}
        </motion.div>
    );
};
