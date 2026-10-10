"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import ProgressBar from "./ProgressBar";
import { playSuccessChime, unlockAudio } from "@/lib/sound";

/* ───────────────────────────────────────────────────────────────
   MODO PRUEBA
   true  → agenda "ficticiamente": no llama al backend, no guarda en Sheets
           ni envía correo/WhatsApp. Útil mientras no conectas el backend.
   false → envía de verdad a NEXT_PUBLIC_API_URL/register
   ─────────────────────────────────────────────────────────────── */
const PRUEBA = true;

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
const EASE = [0.23, 1, 0.32, 1] as const;

type FieldKey = "nombre" | "cedula" | "correo" | "telefono" | "institucion";

type FieldDef = {
  key: FieldKey;
  label: string;
  placeholder: string;
  type?: string;
  inputMode?: "text" | "numeric" | "tel" | "email";
  autoComplete?: string;
  validate: (v: string) => string | null;
};

type Step = { title: string; hint: string; fields: FieldDef[] };

const minLen = (n: number, msg: string) => (v: string) => (v.trim().length < n ? msg : null);

const STEPS: Step[] = [
  {
    title: "¿Cómo te llamas?",
    hint: "Nombre y apellido, tal como aparecerá en tu certificado.",
    fields: [
      {
        key: "nombre",
        label: "Nombre y apellido",
        placeholder: "Nombre y apellido",
        autoComplete: "name",
        validate: (v) =>
          v.trim().split(/\s+/).filter(Boolean).length < 2 ? "Escribe tu nombre y apellido." : null,
      },
    ],
  },
  {
    title: "Tu cédula de identidad",
    hint: "Solo números, sin puntos.",
    fields: [
      {
        key: "cedula",
        label: "Cédula",
        placeholder: "12345678",
        inputMode: "numeric",
        validate: (v) => (/^\d{6,9}$/.test(v.replace(/\D/g, "")) ? null : "Ingresa una cédula válida (6 a 9 dígitos)."),
      },
    ],
  },
  {
    title: "¿A qué correo te escribimos?",
    hint: "Ahí te llegará la confirmación.",
    fields: [
      {
        key: "correo",
        label: "Correo electrónico",
        placeholder: "tucorreo@ejemplo.com",
        type: "email",
        inputMode: "email",
        autoComplete: "email",
        validate: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? null : "Ingresa un correo válido."),
      },
    ],
  },
  {
    title: "Tu número de WhatsApp",
    hint: "Te escribiremos para coordinar el pago.",
    fields: [
      {
        key: "telefono",
        label: "Teléfono",
        placeholder: "0424-0000000",
        type: "tel",
        inputMode: "tel",
        autoComplete: "tel",
        validate: (v) => (/^\d{10,13}$/.test(v.replace(/\D/g, "")) ? null : "Ingresa un teléfono válido."),
      },
    ],
  },
  {
    title: "¿De qué institución vienes?",
    hint: "Universidad, clínica o consultorio.",
    fields: [
      { key: "institucion", label: "Institución", placeholder: "Institución", autoComplete: "organization", validate: minLen(2, "Cuéntanos de dónde vienes.") },
    ],
  },
];

const EMPTY: Record<FieldKey, string> = { nombre: "", cedula: "", correo: "", telefono: "", institucion: "" };

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function sendRegistration(payload: Record<string, string>) {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let msg = "No se pudo completar la inscripción. Intenta de nuevo.";
    try {
      const j = await res.json();
      if (typeof j.detail === "string") msg = j.detail;
    } catch {}
    throw new Error(msg);
  }
}

export default function MultiStepForm() {
  const reduce = useReducedMotion();
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<FieldKey, string>>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [toast, setToast] = useState(false);

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const firstName = values.nombre.trim().split(/\s+/)[0] ?? "";

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(false), 7000);
    return () => clearTimeout(t);
  }, [toast]);

  const variants = {
    initial: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * 24, filter: reduce ? "blur(0px)" : "blur(4px)" }),
    animate: { opacity: 1, x: 0, filter: "blur(0px)", transition: { duration: 0.34, ease: EASE } },
    exit: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * -16, filter: reduce ? "blur(0px)" : "blur(4px)", transition: { duration: 0.16, ease: EASE } }),
  };

  async function next() {
    const found: Partial<Record<FieldKey, string>> = {};
    for (const f of current.fields) {
      const msg = f.validate(values[f.key]);
      if (msg) found[f.key] = msg;
    }
    setErrors(found);
    setFormError(null);
    if (Object.keys(found).length) return;

    if (!isLast) {
      setDirection(1);
      setStep((s) => s + 1);
      return;
    }

    unlockAudio(); // dentro del click, para que el sonido no sea bloqueado
    setSending(true);
    try {
      const payload = Object.fromEntries(Object.entries(values).map(([k, v]) => [k, v.trim()]));
      if (PRUEBA) {
        await sleep(900); // simula el envío
      } else {
        await sendRegistration(payload);
      }
      playSuccessChime();
      setDone(true);
      setToast(true);
    } catch (e) {
      setFormError(e instanceof Error ? e.message : "Ocurrió un error. Intenta de nuevo.");
    } finally {
      setSending(false);
    }
  }

  function back() {
    setErrors({});
    setFormError(null);
    setDirection(-1);
    setStep((s) => Math.max(0, s - 1));
  }

  return (
    <>
      {/* Notificación */}
      <AnimatePresence>
        {toast && (
          <div className="pointer-events-none fixed inset-x-0 top-4 z-[90] flex justify-center">
            <motion.div
              role="status"
              aria-live="polite"
              className="toast pointer-events-auto"
              initial={{ opacity: 0, y: -28, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1, transition: { duration: 0.45, ease: EASE } }}
              exit={{ opacity: 0, y: -16, transition: { duration: 0.2, ease: EASE } }}
            >
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-gradient-to-br from-[#0088cc] to-[#12b886] text-white">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <polyline points="5 12.5 10 17.5 19 7.5" />
                </svg>
              </span>
              <div className="flex-1">
                <p className="font-bold text-[#2c4255]">¡Inscripción agendada!</p>
                <p className="mt-0.5 text-sm text-[#5b6e80]">
                  Recibirás la confirmación por correo y por WhatsApp para realizar el pago.
                </p>
              </div>
              <button type="button" aria-label="Cerrar notificación" onClick={() => setToast(false)} className="text-[#5b6e80] transition-transform active:scale-90">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" aria-hidden>
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {done ? (
        <div className="liquid-glass p-7 sm:p-9">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: EASE }}
            className="mx-auto mb-5 grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-[#0088cc] to-[#12b886] text-white shadow-[0_16px_36px_-10px_rgba(0,136,204,0.55)]"
          >
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <polyline className="check-draw" points="5 12.5 10 17.5 19 7.5" />
            </svg>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: EASE, delay: 0.2 }}>
            <h3 className="text-center text-2xl font-bold tracking-tight text-[#2c4255]">¡Listo, {firstName}!</h3>
            <p className="mt-1.5 text-center text-[#5b6e80]">Tu lugar quedó agendado para el 21 de noviembre.</p>

            <dl className="mt-6 divide-y divide-[#b8d1e1]/60 rounded-2xl border border-[#b8d1e1]/70 bg-white/70 text-sm">
              {[
                ["Nombre", values.nombre.trim()],
                ["Cédula", values.cedula.trim()],
                ["Correo", values.correo.trim()],
                ["Teléfono", values.telefono.trim()],
                ["Institución", values.institucion.trim()],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4 px-4 py-2.5">
                  <dt className="text-[#5b6e80]">{k}</dt>
                  <dd className="break-all text-right font-semibold text-[#2c4255]">{v}</dd>
                </div>
              ))}
            </dl>

            <ol className="mt-5 space-y-2 text-sm text-[#2c4255]">
              <li>1. Te enviamos un correo de confirmación a {values.correo.trim()}.</li>
              <li>2. Te escribiremos por WhatsApp con los datos para realizar el pago.</li>
              <li>3. Instituto Docente de Urología · 21 de noviembre, 2026.</li>
            </ol>

            {PRUEBA && (
              <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-center text-xs font-semibold text-amber-800">
                Modo prueba: no se guardó nada ni se envió correo ni WhatsApp.
              </p>
            )}

            <p className="mt-6 border-t border-[#b8d1e1]/60 pt-4 text-center text-xs text-[#5b6e80]">
              Este reporte fue hecho por{" "}
              <a href="https://instagram.com/synco.ia" target="_blank" rel="noopener noreferrer" className="font-semibold text-[#0088cc] underline-offset-4 hover:underline">
                Synco
              </a>
            </p>
          </motion.div>
        </div>
      ) : (
        <form
          className="liquid-glass p-6 sm:p-9"
          onSubmit={(e) => {
            e.preventDefault();
            void next();
          }}
          noValidate
        >
          {PRUEBA && (
            <p className="mb-5 inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
              🧪 Modo prueba · no se guarda ni se envía nada
            </p>
          )}

          <ProgressBar current={step} total={STEPS.length} />

          <div className="min-h-[220px]">
            <AnimatePresence mode="wait" custom={direction} initial={false}>
              <motion.div key={step} custom={direction} variants={variants} initial="initial" animate="animate" exit="exit">
                <h3 className="text-[1.4rem] font-bold tracking-tight text-[#2c4255]">{current.title}</h3>
                <p className="mb-5 mt-1 text-sm text-[#5b6e80]">{current.hint}</p>

                {current.fields.map((f) => (
                  <div key={f.key}>
                    <input
                      id={f.key}
                      name={f.key}
                      aria-label={f.label}
                      autoFocus
                      className="liquid-glass-input"
                      type={f.type ?? "text"}
                      inputMode={f.inputMode}
                      autoComplete={f.autoComplete}
                      autoCapitalize={f.key === "correo" ? "none" : f.key === "nombre" ? "words" : undefined}
                      placeholder={f.placeholder}
                      value={values[f.key]}
                      aria-invalid={errors[f.key] ? true : undefined}
                      onChange={(e) => {
                        setValues((v) => ({ ...v, [f.key]: e.target.value }));
                        if (errors[f.key]) setErrors((er) => ({ ...er, [f.key]: undefined }));
                      }}
                    />
                    <p className="field-message" role="alert">
                      {errors[f.key]}
                    </p>
                  </div>
                ))}

                {formError && (
                  <p className="field-message" role="alert">
                    {formError}
                  </p>
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="mt-2 flex gap-3">
            {step > 0 && (
              <button type="button" className="glass-button-ghost" onClick={back} disabled={sending}>
                Atrás
              </button>
            )}
            <button type="submit" className={`glass-button flex-1 ${isLast ? "glass-button-brand" : ""}`} disabled={sending}>
              {sending ? <span className="spinner" /> : isLast ? "Inscribirme" : "Continuar"}
            </button>
          </div>
        </form>
      )}
    </>
  );
}