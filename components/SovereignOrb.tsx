"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function SovereignOrb({ hovered }: { hovered: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Create a complex material with a custom shader or using standard with emissive
  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: "#1e3a8a", // Deep blue
      emissive: "#3b82f6", // Bright blue glow
      emissiveIntensity: 0.8,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: false,
    });
  }, []);

  useFrame((state, delta) => {
    if (meshRef.current) {
      // Rotation
      meshRef.current.rotation.y += delta * 0.2;
      meshRef.current.rotation.x += delta * 0.1;

      // Hover Gravity Warp Effect
      const targetScale = hovered ? 1.2 : 1.0;
      const targetIntensity = hovered ? 2.0 : 0.8;
      
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
      
      const mat = meshRef.current.material as THREE.MeshStandardMaterial;
      if (mat) {
         mat.emissiveIntensity = THREE.MathUtils.lerp(mat.emissiveIntensity, targetIntensity, 0.1);
      }
    }
  });

  return (
    <mesh ref={meshRef} material={material}>
      <icosahedronGeometry args={[2, 4]} />
    </mesh>
  );
}
