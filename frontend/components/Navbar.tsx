"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Shield, LayoutDashboard, Info, Home } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

const NavItem = ({ href, label, icon: Icon, isActive }: { href: string; label: string; icon: React.ComponentType<{ className?: string }>; isActive: boolean }) => {
    return (
        <Link href={href} className="relative group">
            <div className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
                isActive ? "bg-neon-orchid/10 text-neon-orchid" : "text-ghost-white/60 hover:text-ghost-white hover:bg-white/5"
            )}>
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium tracking-wide">{label}</span>
            </div>
            {isActive && (
                <motion.div
                    layoutId="nav-glow"
                    className="absolute inset-0 rounded-full bg-neon-orchid/20 blur-md -z-10"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
            )}
        </Link>
    );
};

export const Navbar = () => {
    const pathname = usePathname();

    return (
        <motion.nav
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-6 px-4 pointer-events-none"
        >
            <div className="pointer-events-auto bg-obsidian-core/60 backdrop-blur-xl border border-white/10 rounded-full px-6 py-3 shadow-[0_4px_20px_rgba(0,0,0,0.4)] flex items-center gap-2 relative overflow-hidden group">
                {/* Holographic Sheen */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />

                {/* Logo */}
                <Link href="/" className="mr-6 flex items-center gap-2 group">
                    <div className="w-8 h-8 bg-neon-orchid rounded-lg flex items-center justify-center shadow-[0_0_10px_rgba(255,0,110,0.3)] group-hover:shadow-[0_0_20px_rgba(255,0,110,0.6)] transition-shadow duration-300">
                        <Shield className="text-white w-5 h-5" />
                    </div>
                    <span className="font-orbitron font-bold text-lg tracking-wider text-ghost-white group-hover:text-neon-orchid transition-colors">SON</span>
                </Link>

                {/* Links */}
                <div className="flex items-center gap-1">
                    <NavItem href="/" label="Home" icon={Home} isActive={pathname === "/"} />
                    <NavItem href="/dashboard" label="Scanner" icon={LayoutDashboard} isActive={pathname === "/dashboard"} />
                    <NavItem href="/governance" label="Governance" icon={Shield} isActive={pathname === "/governance"} />
                    <NavItem href="/about" label="Protocol" icon={Info} isActive={pathname === "/about"} />
                </div>

                {/* Status Indicator */}
                <div className="ml-6 pl-6 border-l border-white/10 hidden md:flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_#22c55e]" />
                    <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Mainnet Active</span>
                </div>
            </div>
        </motion.nav>
    );
};
