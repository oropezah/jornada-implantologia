"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { SPEAKERS, initials } from "@/lib/speakers";

const EASE = [0.23, 1, 0.32, 1] as const;

export default function SpeakersSection() {
  const [open, setOpen] = useState<string | null>(null);

  return (
    <>
      <p className="eyebrow mb-3">Ponentes · toca para ver más</p>

      <div className="grid grid-cols-1 items-start gap-2 sm:grid-cols-2">
        {SPEAKERS.map((s, i) => {
          const isOpen = open === s.name;
          return (
            <div key={s.name} className="speaker-item" data-open={isOpen}>
              <button
                type="button"
                className="speaker"
                aria-expanded={isOpen}
                aria-controls={`speaker-${i}`}
                onClick={() => setOpen(isOpen ? null : s.name)}
              >
                <span className="avatar">{initials(s.name)}</span>
                {s.name}
                <svg className="chev" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <path d="M9 6l6 6-6 6" />
                </svg>
              </button>

              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    id={`speaker-${i}`}
                    className="overflow-hidden"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1, transition: { duration: 0.32, ease: EASE } }}
                    exit={{ height: 0, opacity: 0, transition: { duration: 0.2, ease: EASE } }}
                  >
                    <div className="px-4 pb-4 pt-1">
                      <span className="chip">{s.role}</span>

                      <p className="eyebrow mt-4">Ponencia</p>
                      <p className="mt-1 text-sm font-semibold text-[#2c4255]">{s.topic}</p>

                      <p className="eyebrow mt-4">Sobre el ponente</p>
                      <p className="mt-1 text-sm text-[#5b6e80]">{s.bio}</p>

                      <ul className="mt-3 space-y-1.5">
                        {s.highlights.map((h) => (
                          <li key={h} className="flex items-start gap-2.5 text-sm text-[#2c4255]">
                            <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-[#0088cc]" />
                            {h}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </>
  );
}