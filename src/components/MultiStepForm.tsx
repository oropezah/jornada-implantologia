"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import ProgressBar from "./ProgressBar";

type FieldKey = "nombre" | "apellido" | "cedula" | "telefono" | "institucion";

type Step = {
  key: FieldKey;
  title: string;
  hint: string;
  placeholder: string;
  type?: string;
  inputMode?: "text" | "numeric" | "tel";
  autoComplete?: string;
  validate: (v: string) => string | null;
};

const STEPS: Step[] = [
  {
    key: "nombre",
    title: "¿Cómo te llamas?",
    hint: "Tu nombre tal como aparecerá en el certificado.",
    placeholder: "Nombre",
    autoComplete: "given-name",
    validate: (v) => (v.trim().length < 2 ? "Escribe tu nombre." : null),
  },
  {
    key: "apellido",
    title: "¿Y tu apellido?",
    hint: "Puedes escribir uno o los dos.",
    placeholder: "Apellido",
    autoComplete: "family-name",
    validate: (v) => (v.trim().length < 2 ? "Escribe tu apellido." : null),
  },
  {
    key: "cedula",
    title: "Tu cédula de identidad",
    hint: "Solo números, sin puntos.",
    placeholder: "12345678",
    inputMode: "numeric",
    validate: (v) =>
      /^\d{6,9}$/.test(v.replace(/\D/g, "")) ? null : "Ingresa una cédula válida (6 a 9 dígitos).",
  },
  {
    key: "telefono",
    title: "Tu número de teléfono",
    hint: "Para contactarte si hay algún cambio.",
    placeholder: "0424-0000000",
    type: "tel",
    inputMode: "tel",
    autoComplete: "tel",
    validate: (v) =>
      /^\d{10,13}$/.test(v.replace(/\D/g, "")) ? null : "Ingresa un teléfono válido.",
  },
  {
    key: "institucion",
    title: "¿De qué institución vienes?",
    hint: "Universidad, clínica o consultorio.",
    placeholder: "Institución",
    autoComplete: "organization",
    validate: (v) => (v.trim().length < 2 ? "Cuéntanos de dónde vienes." : null),
  },
];

const EASE = [0.23, 1, 0.32, 1] as const;

export default function MultiStepForm() {
  const reduce = useReducedMotion();
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [values, setValues] = useState<Record<FieldKey, string>>({
    nombre: "",
    apellido: "",
    cedula: "",
    telefono: "",
    institucion: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  const variants = {
    initial: (d: number) => ({
      opacity: 0,
      x: reduce ? 0 : d * 24,
      filter: reduce ? "blur(0px)" : "blur(4px)",
    }),
    animate: {
      opacity: 1,
      x: 0,
      filter: "blur(0px)",
      transition: { duration: 0.34, ease: EASE },
    },
    exit: (d: number) => ({
      opacity: 0,
      x: reduce ? 0 : d * -16,
      filter: reduce ? "blur(0px)" : "blur(4px)",
      transition: { duration: 0.16, ease: EASE },
    }),
  };

  async function next() {
    const msg = current.validate(values[current.key]);
    if (msg) {
      setError(msg);
      return;
    }
    setError(null);

    if (!isLast) {
      setDirection(1);
      setStep((s) => s + 1);
      return;
    }

    setSending(true);
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!res.ok) throw new Error("No se pudo completar la inscripción.");
      setDone(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ocurrió un error. Intenta de nuevo.");
    } finally {
      setSending(false);
    }
  }

  function back() {
    setError(null);
    setDirection(-1);
    setStep((s) => Math.max(0, s - 1));
  }

  if (done) {
    return (
      <div className="liquid-glass p-8 text-center sm:p-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: EASE }}
          className="mx-auto mb-6 grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-[#0088cc] to-[#12b886] text-white shadow-[0_16px_36px_-10px_rgba(0,136,204,0.55)]"
        >
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
            <polyline className="check-draw" points="5 12.5 10 17.5 19 7.5" />
          </svg>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: EASE, delay: 0.2 }}
        >
          <h3 className="text-2xl font-bold tracking-tight text-[#2c4255]">
            ¡Listo, {values.nombre.trim()}!
          </h3>
          <p className="mt-2 text-[#5b6e80]">
            Tu inscripción quedó registrada. Nos vemos el 21 de noviembre.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <form
      className="liquid-glass p-6 sm:p-9"
      onSubmit={(e) => {
        e.preventDefault();
        void next();
      }}
      noValidate
    >
      <ProgressBar current={step} total={STEPS.length} />

      <div className="min-h-[190px]">
        <AnimatePresence mode="wait" custom={direction} initial={false}>
          <motion.div
            key={current.key}
            custom={direction}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <label htmlFor={current.key} className="block text-[1.4rem] font-bold tracking-tight text-[#2c4255]">
              {current.title}
            </label>
            <p className="mb-5 mt-1 text-sm text-[#5b6e80]">{current.hint}</p>

            <input
              id={current.key}
              name={current.key}
              autoFocus
              className="liquid-glass-input"
              type={current.type ?? "text"}
              inputMode={current.inputMode}
              autoComplete={current.autoComplete}
              placeholder={current.placeholder}
              value={values[current.key]}
              aria-invalid={error ? true : undefined}
              onChange={(e) => {
                setValues((v) => ({ ...v, [current.key]: e.target.value }));
                if (error) setError(null);
              }}
            />
            <p className="field-message" role="alert">
              {error}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="mt-2 flex gap-3">
        {step > 0 && (
          <button type="button" className="glass-button-ghost" onClick={back} disabled={sending}>
            Atrás
          </button>
        )}
        <button
          type="submit"
          className={`glass-button flex-1 ${isLast ? "glass-button-brand" : ""}`}
          disabled={sending}
        >
          {sending ? <span className="spinner" /> : isLast ? "Inscribirme" : "Continuar"}
        </button>
      </div>
    </form>
  );
}