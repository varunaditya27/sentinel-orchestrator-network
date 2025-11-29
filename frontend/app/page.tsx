"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { SwarmCanvas } from "@/components/SwarmCanvas";
import { Shield, ArrowRight, Lock, Users, Hexagon } from "lucide-react";

// Tech Decoration Component
const TechCorner = ({ className }: { className?: string }) => (
  <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M1 1V6M1 1H6" stroke="currentColor" strokeWidth="2" />
  </svg>
);

export default function LandingPage() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const yHero = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacityHero = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <main ref={containerRef} className="min-h-[200vh] bg-obsidian-core text-ghost-white overflow-x-hidden relative selection:bg-neon-orchid/30">
      <SwarmCanvas />

      {/* Hero Section */}
      <section className="h-screen flex flex-col items-center justify-center px-4 relative overflow-hidden">
        <motion.div
          style={{ y: yHero, opacity: opacityHero }}
          className="max-w-6xl mx-auto text-center space-y-8 z-10"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="inline-flex items-center gap-2 px-6 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-8 shadow-[0_0_20px_rgba(255,0,110,0.2)]"
          >
            <div className="w-2 h-2 bg-neon-orchid rounded-full animate-pulse shadow-[0_0_10px_#FF006E]" />
            <span className="text-xs font-mono tracking-[0.3em] text-neon-orchid uppercase">Sentinel Protocol v1.0</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: "circOut" }}
            className="text-7xl md:text-9xl font-orbitron font-black leading-[0.9] tracking-tighter mix-blend-overlay"
          >
            GOVERNANCE<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/10">GUARD</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl md:text-2xl text-white/60 max-w-3xl mx-auto font-light leading-relaxed"
          >
            The first autonomous agent swarm protecting the <span className="text-electric-cyan font-medium">Cardano Voltaire</span> era from fork exploits and consensus failures.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-col md:flex-row items-center justify-center gap-6 pt-12"
          >
            <Link href="/dashboard">
              <Button className="h-16 px-12 text-lg group relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-neon-orchid to-plasma-pink opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <span className="relative z-10 flex items-center gap-2">
                  Initialize Sentinel
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </span>
              </Button>
            </Link>
            <Link href="/about">
              <Button variant="secondary" className="h-16 px-12 text-lg backdrop-blur-md hover:bg-white/10 border-white/20">
                Protocol Architecture
              </Button>
            </Link>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 1 }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        >
          <span className="text-[10px] font-mono uppercase tracking-widest text-white/30">Scroll to Explore</span>
          <div className="w-[1px] h-12 bg-gradient-to-b from-neon-orchid to-transparent" />
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="min-h-screen py-32 px-4 relative z-20 bg-obsidian-core">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px] opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-obsidian-core via-transparent to-obsidian-core" />

        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {[
              {
                icon: Shield,
                title: "Fork Detection",
                desc: "Real-time analysis of block height divergence across 50+ nodes to prevent minority chain signing.",
                color: "text-neon-orchid",
                gradient: "from-neon-orchid/20 to-transparent"
              },
              {
                icon: Lock,
                title: "Replay Protection",
                desc: "Deep packet inspection of transaction TTL and validity intervals to ensure temporal uniqueness.",
                color: "text-electric-cyan",
                gradient: "from-electric-cyan/20 to-transparent"
              },
              {
                icon: Users,
                title: "Agentic Swarm",
                desc: "Decentralized marketplace where Sentinels hire Oracles and Midnight ZK-Provers on demand.",
                color: "text-amber-warning",
                gradient: "from-amber-warning/20 to-transparent"
              }
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                whileHover={{ y: -10 }}
                className="group relative p-1 rounded-3xl bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-xl border border-white/10 overflow-hidden"
              >
                <TechCorner className="absolute top-4 left-4 text-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                <TechCorner className="absolute top-4 right-4 rotate-90 text-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />

                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

                <div className="relative h-full bg-obsidian-core/90 rounded-[22px] p-8 flex flex-col gap-6">
                  <div className={`w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center ${feature.color} shadow-[0_0_30px_rgba(0,0,0,0.5)] group-hover:scale-110 transition-transform duration-500`}>
                    <feature.icon className="w-8 h-8" />
                  </div>

                  <div>
                    <h3 className="text-2xl font-orbitron font-bold mb-3 group-hover:text-white transition-colors">{feature.title}</h3>
                    <p className="text-white/50 leading-relaxed group-hover:text-white/70 transition-colors">{feature.desc}</p>
                  </div>

                  <div className="mt-auto pt-6 border-t border-white/5 flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white/30 group-hover:text-white/50">
                    <Hexagon className="w-3 h-3" />
                    <span>Module Active</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>
    </main>
  );
}
