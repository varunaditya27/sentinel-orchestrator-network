
import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { Card } from "./ui/Card";
import { Button } from "./ui/Button";
import { X, Download, Share2 } from "lucide-react";
import { Mesh } from "three";

function ShieldModel({ color }: { color: string }) {
    const meshRef = useRef<Mesh>(null!);

    useFrame((state) => {
        if (meshRef.current) {
            meshRef.current.rotation.y += 0.005;
            meshRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.5) * 0.1;
        }
    });

    return (
        <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
            <mesh ref={meshRef}>
                <icosahedronGeometry args={[2.2, 0]} />
                <meshPhysicalMaterial
                    color={color}
                    emissive={color}
                    emissiveIntensity={2}
                    roughness={0.1}
                    metalness={0.8}
                    clearcoat={1}
                    clearcoatRoughness={0.1}
                    wireframe
                />
            </mesh>
            {/* Inner Core */}
            <mesh scale={0.5}>
                <dodecahedronGeometry args={[1.5, 0]} />
                <meshPhysicalMaterial
                    color="#ffffff"
                    emissive={color}
                    emissiveIntensity={0.5}
                    transparent
                    opacity={0.5}
                    roughness={0}
                    metalness={1}
                />
            </mesh>
        </Float>
    );
}

interface ThreatProofCardProps {
    verdict: "SAFE" | "DANGER" | "WARNING";
    proofData?: any;
    onClose: () => void;
}

export const ThreatProofCard = ({ verdict, proofData, onClose }: ThreatProofCardProps) => {
    const isDanger = verdict === "DANGER";
    const isWarning = verdict === "WARNING";
    const color = isDanger ? "#FF006E" : (isWarning ? "#FFD700" : "#00F5FF"); // Gold for WARNING

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <Card className="w-full max-w-4xl h-[600px] flex overflow-hidden relative border-neon-orchid/50">
                <Button
                    variant="secondary"
                    className="absolute top-4 right-4 z-10 !p-2 rounded-full border-none hover:bg-white/10"
                    onClick={onClose}
                >
                    <X className="w-6 h-6" />
                </Button>

                {/* Left Panel: 3D Visualization */}
                <div className="w-1/2 h-full bg-gradient-to-b from-obsidian-core to-void-gray relative">
                    <div className="absolute top-4 left-4 font-orbitron text-white/50 text-sm">
                        THREATPROOF CAPSULE #8847
                    </div>
                    <Canvas className="w-full h-full">
                        <ambientLight intensity={0.5} />
                        <pointLight position={[10, 10, 10]} />
                        <ShieldModel color={color} />
                    </Canvas>
                </div>

                {/* Right Panel: Metadata */}
                <div className="w-1/2 h-full p-8 flex flex-col justify-between bg-obsidian-core/95">
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-orbitron text-white mb-2">EVIDENCE LOG</h3>
                            <div className="h-1 w-20 bg-gradient-to-r from-neon-orchid to-transparent" />
                        </div>

                        <div className="space-y-4 font-mono text-sm">
                            <div className="flex justify-between border-b border-white/10 pb-2">
                                <span className="text-white/50">Proof ID</span>
                                <span className="text-white">{proofData?.proof_id || "PENDING..."}</span>
                            </div>
                            <div className="flex justify-between border-b border-white/10 pb-2">
                                <span className="text-white/50">Timestamp</span>
                                <span className="text-white">{proofData?.signatures?.[0]?.timestamp || "N/A"}</span>
                            </div>
                            <div className="flex justify-between border-b border-white/10 pb-2">
                                <span className="text-white/50">Verdict</span>
                                <span className={isDanger ? "text-neon-orchid" : isWarning ? "text-amber-warning" : "text-electric-cyan"}>
                                    {isDanger ? "UNSAFE_FORK" : isWarning ? "POTENTIAL_RISK" : "VERIFIED_SAFE"}
                                </span>
                            </div>
                            <div className="flex justify-between border-b border-white/10 pb-2">
                                <span className="text-white/50">Merkle Root</span>
                                <span className="text-amber-warning truncate max-w-[150px]">{proofData?.merkle_root || "Calculating..."}</span>
                            </div>
                            <div className="flex justify-between border-b border-white/10 pb-2">
                                <span className="text-white/50">ZK Proof</span>
                                <span className="text-white truncate max-w-[150px]">{proofData?.zk_proof || "Verifying..."}</span>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="text-xs text-white/40 uppercase tracking-wider">Collaborators</div>
                            <div className="flex gap-2">
                                <div className="px-3 py-1 rounded-full bg-neon-orchid/20 text-neon-orchid text-xs border border-neon-orchid/30">SENTINEL-01</div>
                                <div className="px-3 py-1 rounded-full bg-electric-cyan/20 text-electric-cyan text-xs border border-electric-cyan/30">ORACLE-01</div>
                                <div className="px-3 py-1 rounded-full bg-amber-warning/20 text-amber-warning text-xs border border-amber-warning/30">MIDNIGHT-ZK</div>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <Button className="flex-1">
                            <Download className="w-4 h-4 mr-2" />
                            Mint NFT
                        </Button>
                        <Button variant="secondary" className="flex-1">
                            <Share2 className="w-4 h-4 mr-2" />
                            Share
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
};

