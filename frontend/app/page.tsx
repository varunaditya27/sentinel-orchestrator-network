"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { SwarmCanvas } from "@/components/SwarmCanvas";
import { ScrambleText } from "@/components/ScrambleText";
import { HolographicCard } from "@/components/HolographicCard";
import { Shield, ArrowRight, Lock, Users, Hexagon, Vote } from "lucide-react";

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
        {/* Cinematic Background Image */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[url('/hero-bg.png')] bg-cover bg-center opacity-40 mix-blend-screen" />
          <div className="absolute inset-0 bg-gradient-to-b from-obsidian-core/80 via-obsidian-core/50 to-obsidian-core" />
        </div>

        {/* Noise Overlay */}
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none z-10" />

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
            <ScrambleText text="GOVERNANCE" delay={500} />
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/10">
              <ScrambleText text="GUARD" delay={1200} />
            </span>
          </motion.h1>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl md:text-2xl text-white/60 max-w-3xl mx-auto font-light leading-relaxed"
          >
            <p>
              The first <span className="text-electric-cyan font-medium">autonomous agent swarm</span> protecting the Cardano Voltaire era from fork exploits and consensus failures.
            </p>
          </motion.div>

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
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
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
              },
              {
                icon: Vote,
                title: "Governance Autopilot",
                desc: "Analyze 39 proposals in 8 seconds with AI-powered constitutional compliance and sentiment analysis.",
                color: "text-plasma-pink",
                gradient: "from-plasma-pink/20 to-transparent",
                link: "/governance"
              }
            ].map((feature, idx) => {
              const card = (
                <HolographicCard
                  key={idx}
                  className={`rounded-3xl bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-xl border border-white/10 overflow-hidden ${feature.link ? 'cursor-pointer' : ''}`}
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
                </HolographicCard>
              );

              return feature.link ? (
                <Link key={idx} href={feature.link}>
                  {card}
                </Link>
              ) : card;
            })
          </motion.div>
        </div>
      </section>
      {/* Protocol Flow Section */}
      <section className="min-h-screen py-32 px-4 relative z-20 overflow-hidden">
        <div className="absolute inset-0 bg-[url('/protocol-circuit.png')] bg-cover bg-center opacity-20 mix-blend-screen fixed" />
        <div className="absolute inset-0 bg-gradient-to-b from-obsidian-core via-obsidian-core/90 to-obsidian-core" />

        <div className="max-w-7xl mx-auto relative z-10 space-y-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center space-y-6"
          >
            <h2 className="text-4xl md:text-6xl font-orbitron font-bold">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-orchid to-electric-cyan">AUTONOMOUS</span> DEFENSE
            </h2>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              A millisecond-scale choreography of AI agents, cryptographic proofs, and decentralized consensus checks.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            {/* Step 1: Sentinel */}
            <HolographicCard className="p-8 rounded-3xl bg-black/40 border border-neon-orchid/20 backdrop-blur-xl">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-xl bg-neon-orchid/10 flex items-center justify-center border border-neon-orchid/30 shrink-0">
                  <Shield className="w-6 h-6 text-neon-orchid" />
                </div>
                <div className="space-y-4">
                  <h3 className="text-2xl font-orbitron font-bold text-neon-orchid">01. SENTINEL INGESTION</h3>
                  <p className="text-white/70 leading-relaxed">
                    The user pastes a transaction CBOR. The <strong className="text-white">Sentinel Agent</strong> immediately parses OpCodes, checking for <span className="text-neon-orchid">Protocol V3 compliance</span> and validity intervals (TTL).
                  </p>
                  <div className="text-xs font-mono text-white/40 bg-white/5 p-3 rounded border border-white/10">
                    {`> PARSE_CBOR(tx_payload)`}<br />
                    {`> CHECK_COMPLIANCE(v3_params)`}<br />
                    {`> VERDICT: PENDING_NETWORK_CHECK`}
                  </div>
                </div>
              </div>
            </HolographicCard>

            {/* Step 2: Agent Economy */}
            <HolographicCard className="p-8 rounded-3xl bg-black/40 border border-electric-cyan/20 backdrop-blur-xl md:translate-y-12">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-xl bg-electric-cyan/10 flex items-center justify-center border border-electric-cyan/30 shrink-0">
                  <Users className="w-6 h-6 text-electric-cyan" />
                </div>
                <div className="space-y-4">
                  <h3 className="text-2xl font-orbitron font-bold text-electric-cyan">02. THE HIRE</h3>
                  <p className="text-white/70 leading-relaxed">
                    Sentinel triggers a <strong className="text-white">HIRE_REQUEST</strong>. Using the <span className="text-electric-cyan">Masumi Protocol</span>, funds are locked in escrow. The job is cryptographically signed via DID.
                  </p>
                  <div className="text-xs font-mono text-white/40 bg-white/5 p-3 rounded border border-white/10">
                    {`> LOCK_ESCROW(1.0 ADA)`}<br />
                    {`> SIGN_CONTRACT(did:sentinel:xyz)`}<br />
                    {`> DISPATCH_JOB(target: ORACLE)`}
                  </div>
                </div>
              </div>
            </HolographicCard>

            {/* Step 3: Oracle Consensus */}
            <HolographicCard className="p-8 rounded-3xl bg-black/40 border border-plasma-pink/20 backdrop-blur-xl">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-xl bg-plasma-pink/10 flex items-center justify-center border border-plasma-pink/30 shrink-0">
                  <ArrowRight className="w-6 h-6 text-plasma-pink" />
                </div>
                <div className="space-y-4">
                  <h3 className="text-2xl font-orbitron font-bold text-plasma-pink">03. CONSENSUS CHECK</h3>
                  <p className="text-white/70 leading-relaxed">
                    The <strong className="text-white">Oracle Agent</strong> queries 50+ global nodes. It compares block height and hash to detect <span className="text-plasma-pink">Minority Forks</span> or &quot;Ghost Chains&quot;.
                  </p>
                  <div className="text-xs font-mono text-white/40 bg-white/5 p-3 rounded border border-white/10">
                    {`> QUERY_NODES(n=50)`}<br />
                    {`> COMPARE_TIP(local_height, global_avg)`}<br />
                    {`> DETECT_DIVERGENCE(diff > 3 blocks)`}
                  </div>
                </div>
              </div>
            </HolographicCard>

            {/* Step 4: Midnight Proof */}
            <HolographicCard className="p-8 rounded-3xl bg-black/40 border border-amber-warning/20 backdrop-blur-xl md:translate-y-12">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-xl bg-amber-warning/10 flex items-center justify-center border border-amber-warning/30 shrink-0">
                  <Lock className="w-6 h-6 text-amber-warning" />
                </div>
                <div className="space-y-4">
                  <h3 className="text-2xl font-orbitron font-bold text-amber-warning">04. ZK-PROOF & SETTLEMENT</h3>
                  <p className="text-white/70 leading-relaxed">
                    <strong className="text-white">Midnight</strong> generates a Zero-Knowledge Proof of the threat. The verdict is settled via <span className="text-amber-warning">Hydra</span>, blocking the transaction if unsafe.
                  </p>
                  <div className="text-xs font-mono text-white/40 bg-white/5 p-3 rounded border border-white/10">
                    {`> GEN_ZKP(threat_evidence)`}<br />
                    {`> VERDICT: DANGER_REPLAY_ATTACK`}<br />
                    {`> BLOCK_TX()`}
                  </div>
                </div>
              </div>
            </HolographicCard>
          </div>
        </div>
      </section>
    </main>
  );
}
