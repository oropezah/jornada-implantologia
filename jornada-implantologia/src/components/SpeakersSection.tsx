"use client";

import { motion } from "framer-motion";
import { SPEAKERS } from "@/lib/speakers";

export default function SpeakersSection() {
  // Duplicamos la lista para crear el bucle infinito sin saltos visuales
  const doubledSpeakers = [...SPEAKERS, ...SPEAKERS];

  return (
    <div className="relative w-full overflow-hidden py-4">
      {/* Sombras laterales para difuminar la entrada y salida de los nombres */}
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-[#f8fafc] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-[#f8fafc] to-transparent" />

      <motion.div
        className="flex w-max items-center gap-6"
        animate={{ x: ["0%", "-50%"] }}
        transition={{
          repeat: Infinity,
          ease: "linear",
          duration: 25, // Controla la velocidad: a mayor número, más lento pasa
        }}
      >
        {doubledSpeakers.map((s, idx) => (
          <div
            key={`${s.name}-${idx}`}
            className="flex items-center gap-3 rounded-2xl border border-[#b8d1e1]/60 bg-white/70 px-5 py-3 shadow-sm backdrop-blur-md"
          >
            <span className="flex h-2 w-2 rounded-full bg-[#0088cc]" />
            <span className="whitespace-nowrap font-semibold tracking-tight text-[#2c4255]">
              {s.name}
            </span>
          </div>
        ))}
      </motion.div>
    </div>
  );
}