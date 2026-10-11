"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

// Se carga solo en el navegador y después de la bienvenida.
const Iridescence = dynamic(() => import("./Iridescence"), { ssr: false });

// Color #2a457f convertido a RGB normalizado (0 a 1)
const COLOR: [number, number, number] = [0.165, 0.27, 0.498];

export default function BackgroundFX() {
  const [on, setOn] = useState(false);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const conn = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;
    if (reduce || conn?.saveData) return;

    const start = () => setOn(true);
    if (document.documentElement.dataset.welcome !== "pending") {
      start();
      return;
    }
    window.addEventListener("welcome:done", start, { once: true });
    return () => window.removeEventListener("welcome:done", start);
  }, []);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* Fondo degradado base */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#eef2f8] via-[#f0f4f8] to-[#e4eef6]" />
      {on && (
        <motion.div
          className="absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.55 }}
          transition={{ duration: 1.6, ease: "easeOut" }}
        >
          <Iridescence 
            color={COLOR} 
            speed={0.6} 
            amplitude={0.1} 
            mouseReact={false} 
            brightness={1.95} 
          />
        </motion.div>
      )}
      {/* Velo para legibilidad del texto */}
      <div className="absolute inset-0 bg-[radial-gradient(70%_55%_at_50%_0%,rgba(255,255,255,0.75),rgba(255,255,255,0.15)_70%)]" />
    </div>
  );
}