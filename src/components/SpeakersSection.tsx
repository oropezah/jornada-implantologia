"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { SPEAKERS, initials, type Speaker } from "@/lib/speakers";

const EASE = [0.23, 1, 0.32, 1] as const;

export default function SpeakersSection() {
  const [selected, setSelected] = useState<Speaker | null>(null);

  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setSelected(null);
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [selected]);

  return (
    <>
      <p className="eyebrow mb-3">Ponentes · toca para ver más</p>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {SPEAKERS.map((s) => (
          <button key={s.name} type="button" className="speaker" onClick={() => setSelected(s)}>
            <span className="avatar">{initials(s.name)}</span>
            {s.name}
            <svg className="chev" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M9 6l6 6-6 6" />
            </svg>
          </button>
        ))}
      </div>

      <AnimatePresence>
        {selected && (
          <div className="fixed inset-0 z-[80] flex items-end justify-center sm:items-center sm:p-6">
            <motion.div
              className="absolute inset-0 bg-[#1e2e3d]/40 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, transition: { duration: 0.25 } }}
              exit={{ opacity: 0, transition: { duration: 0.15 } }}
              onClick={() => setSelected(null)}
            />
            <motion.div
              role="dialog"
              aria-modal="true"
              aria-label={selected.name}
              className="relative w-full max-h-[88dvh] overflow-y-auto rounded-t-[28px] bg-white p-7 shadow-[0_30px_80px_-20px_rgba(44,66,85,0.45)] sm:max-w-md sm:rounded-[28px]"
              initial={{ opacity: 0, y: 48, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1, transition: { duration: 0.38, ease: EASE } }}
              exit={{ opacity: 0, y: 24, transition: { duration: 0.18, ease: EASE } }}
            >
              <button
                type="button"
                autoFocus
                aria-label="Cerrar"
                onClick={() => setSelected(null)}
                className="absolute right-4 top-4 grid h-9 w-9 place-items-center rounded-full bg-[#f0f4f8] text-[#2c4255] transition-transform active:scale-90"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" aria-hidden>
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>

              <div className="avatar avatar-lg">{initials(selected.name)}</div>
              <h3 className="mt-4 text-2xl font-bold tracking-tight text-[#2c4255]">{selected.name}</h3>
              <span className="chip mt-2">{selected.role}</span>

              <p className="eyebrow mt-6">Ponencia</p>
              <p className="mt-1.5 font-semibold text-[#2c4255]">{selected.topic}</p>

              <p className="eyebrow mt-5">Sobre el ponente</p>
              <p className="mt-1.5 text-[0.95rem] text-[#5b6e80]">{selected.bio}</p>

              <ul className="mt-4 space-y-2">
                {selected.highlights.map((h) => (
                  <li key={h} className="flex items-start gap-2.5 text-sm text-[#2c4255]">
                    <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-[#0088cc]" />
                    {h}
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}