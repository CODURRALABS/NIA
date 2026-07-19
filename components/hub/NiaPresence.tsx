"use client";

import { useEffect, useRef } from "react";

export default function NiaPresence() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // A simple fluid/particle animation representing NIA's "thought process"
        let animationFrameId: number;
        const particles: { x: number; y: number; vx: number; vy: number; radius: number }[] = [];
        const particleCount = 50;

        const resizeCanvas = () => {
            canvas.width = canvas.parentElement?.clientWidth || 400;
            canvas.height = canvas.parentElement?.clientHeight || 400;
        };
        window.addEventListener("resize", resizeCanvas);
        resizeCanvas();

        // Initialize particles
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                radius: Math.random() * 2 + 1,
            });
        }

        const draw = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Center pulsating core
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const time = Date.now() * 0.001;
            const coreRadius = 40 + Math.sin(time * 2) * 10;

            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, coreRadius * 2);
            gradient.addColorStop(0, "rgba(59, 130, 246, 0.8)"); // Blue-500
            gradient.addColorStop(1, "rgba(59, 130, 246, 0)");

            ctx.beginPath();
            ctx.arc(centerX, centerY, coreRadius * 2, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.fill();

            // Particles
            ctx.fillStyle = "rgba(147, 197, 253, 0.6)"; // Blue-300
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();

                // Connect particles near core
                const distToCore = Math.hypot(p.x - centerX, p.y - centerY);
                if (distToCore < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(centerX, centerY);
                    ctx.strokeStyle = `rgba(96, 165, 250, ${1 - distToCore / 150})`; // Blue-400
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            });

            animationFrameId = requestAnimationFrame(draw);
        };

        draw();

        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener("resize", resizeCanvas);
        };
    }, []);

    return (
        <div className="relative w-full h-full flex items-center justify-center z-10">
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                </div>
            </div>
        </div>
    );
}
