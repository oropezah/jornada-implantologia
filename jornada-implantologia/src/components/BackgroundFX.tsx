"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

// Se carga solo en el navegador y después de la bienvenida.
const Iridescence = dynamic(() => import("./Iridescence"), { ssr: false });

// Blanco puro en RGB (1, 1, 1)
const COLOR: [number, number, number] = [1, 1, 1];

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
      {/* Fondo degradado claro neutro */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#f8fafc] via-[#f1f5f9] to-[#e2e8f0]" />
      {on && (
        <motion.div
          className="absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.65 }}
          transition={{ duration: 1.6, ease: "easeOut" }}
        >
          <Iridescence 
            color={COLOR} 
            speed={0.5} 
            amplitude={0.08} 
            mouseReact={false} 
            brightness={1.2}
            saturation={0.3}
          />
        </motion.div>
      )}
      {/* Velo para legibilidad perfecta de todos los textos */}
      <div className="absolute inset-0 bg-[radial-gradient(70%_55%_at_50%_0%,rgba(255,255,255,0.85),rgba(255,255,255,0.3)_70%)]" />
    </div>
  );
}