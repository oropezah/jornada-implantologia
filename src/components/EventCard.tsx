"use client";

import { useEffect, useState } from "react";
import { animate, motion } from "framer-motion";
import { EVENT, calendarUrl, mapsUrl } from "@/lib/event";

const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

function CountUp({ to }: { to: number }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const c = animate(0, to, { duration: 1.6, ease: EASE, delay: 0.3, onUpdate: (v) => setN(Math.round(v)) });
    return () => c.stop();
  }, [to]);
  return <span className="tabular-nums">{n}</span>;
}

export default function EventCard() {
  const [days, setDays] = useState<number | null>(null);

  useEffect(() => {
    setDays(Math.max(0, Math.ceil((EVENT.date.getTime() - Date.now()) / 86_400_000)));
  }, []);

  return (
    <div className="liquid-glass p-5 sm:p-6">
      <div className="flex items-stretch gap-5">
        <div className="relative grid w-[88px] shrink-0 place-items-center overflow-hidden rounded-2xl bg-gradient-to-br from-[#2c4255] to-[#0088cc] px-2 py-3 text-center text-white shadow-[0_14px_28px_-12px_rgba(0,136,204,0.6)]">
          <span className="text-[0.62rem] font-semibold uppercase tracking-[0.2em] text-white/70">Sábado</span>
          <span className="-mt-1 text-[2.7rem] font-bold leading-none tracking-tight">21</span>
          <span className="text-[0.7rem] font-semibold uppercase tracking-[0.16em]">Nov 2026</span>
          <motion.span
            aria-hidden
            className="pointer-events-none absolute inset-y-0 -left-1/2 w-1/2 -skew-x-12 bg-white/25"
            initial={{ x: "-100%" }}
            animate={{ x: "500%" }}
            transition={{ duration: 1.4, ease: EASE, delay: 0.8 }}
          />
        </div>

        <div className="min-w-0 flex-1">
          <p className="eyebrow">Sede</p>
          <p className="mt-1.5 text-lg font-bold leading-tight tracking-tight text-[#2c4255]">{EVENT.place}</p>
          <p className="mt-0.5 text-sm text-[#5b6e80]">Universidad de Carabobo</p>
          <a
            href={mapsUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-[#0088cc] underline-offset-4 hover:underline"
          >
            Ver mapa
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M7 17L17 7M9 7h8v8" />
            </svg>
          </a>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#b8d1e1]/60 pt-4">
        <p className="min-h-[1.75rem] text-sm text-[#5b6e80]">
          {days === null ? null : days > 0 ? (
            <>
              Faltan <b className="text-xl text-[#2c4255]"><CountUp to={days} /></b> días
            </>
          ) : (
            <b className="text-[#2c4255]">¡Es hoy!</b>
          )}
        </p>
        <a
          href={calendarUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-full border border-[#b8d1e1] bg-white/70 px-4 py-2 text-sm font-semibold text-[#2c4255] transition-[transform,background-color] duration-200 hover:bg-white active:scale-95"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <rect x="3" y="5" width="18" height="16" rx="3" />
            <path d="M8 3v4M16 3v4M3 10h18" />
          </svg>
          Agregar al calendario
        </a>
      </div>
    </div>
  );
}