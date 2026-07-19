"use client";

import React from "react";

export default function SovereignOrb() {
    return (
        <div className="relative w-full h-full flex items-center justify-center bg-black overflow-hidden select-none">
            <button
                className="relative flex items-center justify-center transition-all duration-700 hover:scale-105 active:scale-95 group pointer-events-auto"
            >
                <div className="flex flex-col items-center gap-6">
                    <div
                        className="relative flex items-center justify-center"
                        style={{ width: '260px', height: '260px' }}
                    >
                        <svg
                            className="absolute inset-0 w-full h-full -z-10"
                            viewBox="0 0 260 260"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <defs>
                                <radialGradient id="g1" cx="30%" cy="30%">
                                    <stop offset="0%" stopColor="#ffffff" stopOpacity="0.9"></stop>
                                    <stop offset="20%" stopColor="#6ee7b7" stopOpacity="0.28"></stop>
                                    <stop offset="70%" stopColor="#0b1020" stopOpacity="0.02"></stop>
                                </radialGradient>
                                <filter id="blur" x="-20%" y="-20%" width="140%" height="140%">
                                    <feGaussianBlur stdDeviation="10" result="b"></feGaussianBlur>
                                    <feBlend in="SourceGraphic" in2="b"></feBlend>
                                </filter>
                            </defs>

                            <circle
                                cx="130"
                                cy="130"
                                r="90"
                                fill="url(#g1)"
                                opacity="0.9"
                                filter="url(#blur)"
                            ></circle>

                            <g shadow-inner="true" className="opacity-60" transform="translate(130,130)">
                                <ellipse
                                    cx="0"
                                    cy="0"
                                    rx="110"
                                    ry="110"
                                    fill="none"
                                    stroke="#60a5fa"
                                    strokeOpacity="0.06"
                                    strokeWidth="2"
                                >
                                    <animateTransform
                                        attributeName="transform"
                                        type="rotate"
                                        from="0 0 0"
                                        to="360 0 0"
                                        dur="18s"
                                        repeatCount="indefinite"
                                    ></animateTransform>
                                </ellipse>
                            </g>

                            <g className="opacity-50" transform="translate(130,130)">
                                <ellipse
                                    cx="0"
                                    cy="0"
                                    rx="85"
                                    ry="85"
                                    fill="none"
                                    stroke="#6ee7b7"
                                    strokeOpacity="0.05"
                                    strokeWidth="2"
                                >
                                    <animateTransform
                                        attributeName="transform"
                                        type="rotate"
                                        from="0 0 0"
                                        to="360 0 0"
                                        dur="10s"
                                        repeatCount="indefinite"
                                    ></animateTransform>
                                </ellipse>
                            </g>

                            <g transform="translate(130,130)" className="opacity-40">
                                <circle
                                    r="30"
                                    fill="none"
                                    stroke="#6ee7b7"
                                    strokeOpacity="0.08"
                                    strokeWidth="2"
                                ></circle>
                                <circle
                                    r="20"
                                    fill="none"
                                    stroke="#60a5fa"
                                    strokeOpacity="0.06"
                                    strokeWidth="1.6"
                                ></circle>
                            </g>
                        </svg>

                        <div
                            className="rounded-full flex items-center justify-center bg-gradient-to-tr from-white/80 via-[#614BC6]/40 to-[#0b1020]/80 shadow-[0_20px_60px_rgba(0,0,0,0.6)] animate-pulse"
                            style={{ width: '220px', height: '220px' }}
                        >
                            <div
                                className="rounded-full flex items-center justify-center bg-[radial-gradient(ellipse_at_center,_#0b1020_0%,_#614BC6_40%,_#E3EDF6_90%)] backdrop-blur-md shadow-inner w-[78%] h-[78%] transition-all duration-700 group-hover:brightness-125 group-hover:scale-105"
                            >
                                <svg
                                    className="w-3/5 h-3/5"
                                    viewBox="0 0 100 60"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <rect
                                        x="10"
                                        y="10"
                                        width="8"
                                        height="40"
                                        rx="2"
                                        fill="url(#barGrad)"
                                        style={{ transformOrigin: "14px 40px" }}
                                    >
                                        <animateTransform
                                            attributeName="transform"
                                            type="scale"
                                            values="1 0.3;1 1;1 0.3"
                                            dur="1.2s"
                                            repeatCount="indefinite"
                                            begin="-0.9s"
                                        ></animateTransform>
                                    </rect>
                                    <rect
                                        x="26"
                                        y="16"
                                        width="8"
                                        height="34"
                                        rx="2"
                                        fill="url(#barGrad)"
                                        style={{ transformOrigin: "30px 40px" }}
                                    >
                                        <animateTransform
                                            attributeName="transform"
                                            type="scale"
                                            values="1 0.35;1 1;1 0.35"
                                            dur="1.2s"
                                            repeatCount="indefinite"
                                            begin="-0.6s"
                                        ></animateTransform>
                                    </rect>
                                    <rect
                                        x="42"
                                        y="6"
                                        width="8"
                                        height="44"
                                        rx="2"
                                        fill="url(#barGrad)"
                                        style={{ transformOrigin: "46px 40px" }}
                                    >
                                        <animateTransform
                                            attributeName="transform"
                                            type="scale"
                                            values="1 0.25;1 1;1 0.25"
                                            dur="1.2s"
                                            repeatCount="indefinite"
                                            begin="-0.3s"
                                        ></animateTransform>
                                    </rect>
                                    <rect
                                        x="58"
                                        y="14"
                                        width="8"
                                        height="36"
                                        rx="2"
                                        fill="url(#barGrad)"
                                        style={{ transformOrigin: "62px 40px" }}
                                    >
                                        <animateTransform
                                            attributeName="transform"
                                            type="scale"
                                            values="1 0.4;1 1;1 0.4"
                                            dur="1.2s"
                                            repeatCount="indefinite"
                                            begin="0s"
                                        ></animateTransform>
                                    </rect>
                                    <rect
                                        x="74"
                                        y="8"
                                        width="8"
                                        height="42"
                                        rx="2"
                                        fill="url(#barGrad)"
                                        style={{ transformOrigin: "78px 40px" }}
                                    >
                                        <animateTransform
                                            attributeName="transform"
                                            type="scale"
                                            values="1 0.28;1 1;1 0.28"
                                            dur="1.2s"
                                            repeatCount="indefinite"
                                            begin="0.3s"
                                        ></animateTransform>
                                    </rect>

                                    <defs>
                                        <linearGradient id="barGrad" x1="0" x2="0" y1="0" y2="1">
                                            <stop
                                                offset="0%"
                                                stopColor="#a5f3fc"
                                                stopOpacity="0.95"
                                            ></stop>
                                            <stop
                                                offset="100%"
                                                stopColor="#1e3a8a"
                                                stopOpacity="0.25"
                                            ></stop>
                                        </linearGradient>
                                    </defs>
                                </svg>
                            </div>
                        </div>

                        <span
                            className="absolute rounded-full pointer-events-none mix-blend-screen"
                            style={{ width: '320px', height: '320px', left: '-30px', top: '-30px', filter: 'blur(28px)', opacity: 0.35, background: 'radial-gradient(circle at 30% 30%, rgba(110,231,183,0.18), transparent 30%)' }}
                        ></span>
                    </div>
                </div>
            </button>
        </div>
    );
}
