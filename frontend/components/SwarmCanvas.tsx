"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as random from "maath/random/dist/maath-random.cjs";

import { Points as ThreePoints } from "three";

function Swarm(props: React.ComponentProps<typeof Points>) {
    const ref = useRef<ThreePoints>(null);
    const [sphere] = useMemo(() => {
        const data = random.inSphere(new Float32Array(5000 * 3), { radius: 1.5 }) as Float32Array;
        return [data];
    }, []);

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 10;
            ref.current.rotation.y -= delta / 15;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
                <PointMaterial
                    transparent
                    color="#FF006E"
                    size={0.005}
                    sizeAttenuation={true}
                    depthWrite={false}
                />
            </Points>
        </group>
    );
}

export const SwarmCanvas = () => {
    return (
        <div className="absolute inset-0 -z-10">
            <Canvas camera={{ position: [0, 0, 1] }}>
                <Swarm />
            </Canvas>
        </div>
    );
};
