"use client";

import { motion } from "framer-motion";
import SyncoPitch from "./SyncoPitch";
import { EVENT, calendarUrl } from "@/lib/event";

const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

type Props = { nombre: string; cedula: string; correo: string; institucion: string; prueba: boolean };

const PARTICLES = Array.from({ length: 14 }, (_, i) => {
  const a = (i / 14) * Math.PI * 2;
  const r = 62 + (i % 3) * 14;
  return { x: Math.cos(a) * r, y: Math.sin(a) * r, c: i % 2 ? "#0088cc" : "#12b886", s: 5 + (i % 3) * 2 };
});

const fadeUp = (delay: number) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: EASE, delay },
});

export default function RegistrationSuccess({ nombre, cedula, correo, institucion, prueba }: Props) {
  const first = nombre.trim().split(/\s+/)[0] ?? "";

  const steps = [
    { t: "Comprobante recibido", d: "Ya está en nuestro sistema.", state: "done" },
    { t: "Verificando tu pago", d: "Lo revisamos manualmente.", state: "now" },
    { t: "Confirmación por correo", d: `Te escribimos a ${correo}.`, state: "next" },
  ];

  function invite() {
    const text = `Te comparto la ${EVENT.title} (21 de noviembre, UC). Inscríbete aquí: ${window.location.origin}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank", "noopener,noreferrer");
  }

  return (
    <div className="liquid-glass p-6 sm:p-8">
      {/* Check con explosión de partículas */}
      <div className="relative mx-auto mb-5 grid h-20 w-20 place-items-center">
        {PARTICLES.map((p, i) => (
          <motion.span
            key={i}
            aria-hidden
            className="absolute rounded-full"
            style={{ width: p.s, height: p.s, background: p.c }}
            initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
            animate={{ x: p.x, y: p.y, opacity: 0, scale: 0.4 }}
            transition={{ duration: 0.9, ease: EASE, delay: 0.25 }}
          />
        ))}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: EASE }}
          className="grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-[#0088cc] to-[#12b886] text-white shadow-[0_16px_36px_-10px_rgba(0,136,204,0.55)]"
        >
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <polyline className="check-draw" points="5 12.5 10 17.5 19 7.5" />
          </svg>
        </motion.div>
      </div>

      <motion.div {...fadeUp(0.2)} className="text-center">
        <h3 className="text-2xl font-bold tracking-tight text-[#2c4255]">¡Listo, {first}!</h3>
        <p className="mt-1.5 text-[#5b6e80]">Tu inscripción quedó registrada.</p>
        <span className="mt-3 inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-500" />
          </span>
          Pago por verificar
        </span>
      </motion.div>

      {/* Pase del asistente */}
      <motion.div {...fadeUp(0.35)} className="mt-6 overflow-hidden rounded-2xl border border-[#b8d1e1]/70 bg-white/85 shadow-[0_18px_40px_-20px_rgba(44,66,85,0.35)]">
        <div className="flex items-center justify-between bg-gradient-to-r from-[#2c4255] to-[#0088cc] px-5 py-3 text-white">
          <span className="text-xs font-semibold uppercase tracking-[0.18em]">{EVENT.short}</span>
          <span className="text-xs font-medium text-white/80">Asistente</span>
        </div>
        <div className="px-5 py-4">
          <p className="text-lg font-bold leading-tight text-[#2c4255]">{nombre.trim()}</p>
          <p className="text-sm text-[#5b6e80]">{institucion.trim()}</p>
          <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-xs text-[#5b6e80]">Cédula</dt>
              <dd className="font-semibold text-[#2c4255]">{cedula.trim()}</dd>
            </div>
            <div className="min-w-0">
              <dt className="text-xs text-[#5b6e80]">Correo</dt>
              <dd className="truncate font-semibold text-[#2c4255]">{correo.trim()}</dd>
            </div>
          </dl>
        </div>
        <div className="flex justify-between gap-3 border-t border-dashed border-[#b8d1e1] px-5 py-3 text-xs text-[#5b6e80]">
          <span>21 Nov 2026</span>
          <span className="text-right">{EVENT.place}</span>
        </div>
      </motion.div>

      {/* Línea de tiempo */}
      <motion.ol {...fadeUp(0.5)} className="mt-6">
        {steps.map((s) => (
          <li
            key={s.t}
            className="relative pb-5 pl-9 last:pb-0 before:absolute before:left-[11px] before:top-6 before:h-full before:w-px before:bg-[#b8d1e1] last:before:hidden"
          >
            <span
              className={
                "absolute left-0 top-0 grid h-6 w-6 place-items-center rounded-full " +
                (s.state === "done"
                  ? "bg-[#12b886] text-white"
                  : s.state === "now"
                    ? "border-2 border-[#0088cc] bg-white"
                    : "border-2 border-[#b8d1e1] bg-white")
              }
            >
              {s.state === "done" && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <polyline points="5 12.5 10 17.5 19 7.5" />
                </svg>
              )}
              {s.state === "now" && <span className="h-2 w-2 animate-pulse rounded-full bg-[#0088cc]" />}
            </span>
            <p className="text-sm font-semibold text-[#2c4255]">{s.t}</p>
            <p className="text-xs text-[#5b6e80]">{s.d}</p>
          </li>
        ))}
      </motion.ol>

      <motion.div {...fadeUp(0.65)} className="mt-6 flex flex-col gap-3 sm:flex-row">
        <a href={calendarUrl()} target="_blank" rel="noopener noreferrer" className="glass-button glass-button-brand shine flex-1">
          Agregar al calendario
        </a>
        <button type="button" onClick={invite} className="glass-button-ghost inline-flex flex-1 items-center justify-center">
          Invitar a un colega
        </button>
      </motion.div>

      {prueba && (
        <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-center text-xs font-semibold text-amber-800">
          Modo prueba: no se guardó nada.
        </p>
      )}

      <motion.div {...fadeUp(0.8)} className="mt-6">
        <SyncoPitch />
      </motion.div>

      <p className="mt-6 border-t border-[#b8d1e1]/60 pt-4 text-center text-xs text-[#5b6e80]">
        Este reporte fue hecho por{" "}
        <a href="https://instagram.com/synco.ia" target="_blank" rel="noopener noreferrer" className="font-semibold text-[#0088cc] underline-offset-4 hover:underline">
          Synco
        </a>
      </p>
    </div>
  );
}