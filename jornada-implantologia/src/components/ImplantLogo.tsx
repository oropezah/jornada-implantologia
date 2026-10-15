"use client";

import { motion } from "framer-motion";

const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

const THREADS = [
  "M36.2 110Q60 119 83.8 110",
  "M38.8 124Q60 133 81.2 124",
  "M41.3 138Q60 147 78.7 138",
  "M43.9 152Q60 161 76.1 152",
  "M46.5 166Q60 175 73.5 166",
  "M49 180Q60 188 71 180",
];

export default function ImplantLogo({ className, delay = 0 }: { className?: string; delay?: number }) {
  const draw = (d: number, dur: number) => ({
    initial: { pathLength: 0, opacity: 0 },
    animate: { pathLength: 1, opacity: 1 },
    transition: { duration: dur, delay: delay + d, ease: EASE },
  });

  return (
    <svg viewBox="0 0 120 210" fill="none" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
      <motion.path d="M16 78C8 46 14 16 40 12c10-2 16 4 20 12 4-8 10-14 20-12 26 4 32 34 24 66" stroke="#2c4255" strokeWidth="3.4" {...draw(0, 1.0)} />
      <motion.path d="M30 90c8 6 52 6 60 0" stroke="#2c4255" strokeWidth="3" {...draw(0.7, 0.5)} />
      <motion.path d="M34 98L52 196c1 4 4 6 8 6s7-2 8-6l18-98" stroke="#2c4255" strokeWidth="3.4" {...draw(0.8, 1.0)} />
      {THREADS.map((t, i) => (
        <motion.path key={t} d={t} stroke="#2c4255" strokeWidth="3" {...draw(1.1 + i * 0.1, 0.45)} />
      ))}
      <motion.path d="M24 96C46 114 82 90 98 114" stroke="#0088cc" strokeWidth="3" {...draw(1.4, 0.8)} />
    </svg>
  );
}