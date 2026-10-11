"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import ProgressBar from "./ProgressBar";
import RegistrationSuccess from "./RegistrationSuccess";
import { playSuccessChime, unlockAudio } from "@/lib/sound";

const PRUEBA = false;

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "https://jornada-implantologia.onrender.com").replace(/\/$/, "");
const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

const PAGO = [
  { label: "Cédula", value: "26.581.836", copy: "26581836" },
  { label: "Teléfono", value: "04144099988", copy: "04144099988" },
  { label: "Banco", value: "Banco de Venezuela", copy: "Banco de Venezuela" },
];

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

type Step = { title: string; hint: string; fields: FieldDef[]; kind?: "pago" };

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
    title: "Tu número de teléfono",
    hint: "Para contactarte si hay algún cambio.",
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
  {
    title: "Realiza tu pago",
    hint: "Haz el pago móvil y sube el comprobante para confirmar tu lugar.",
    fields: [],
    kind: "pago",
  },
];

const EMPTY: Record<FieldKey, string> = { nombre: "", cedula: "", correo: "", telefono: "", institucion: "" };

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function compressImage(file: File, maxSide = 1280, quality = 0.8): Promise<File> {
  return new Promise((resolve) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(file);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => {
          if (!blob || blob.size >= file.size) return resolve(file);
          resolve(new File([blob], file.name.replace(/\.\w+$/, "") + ".jpg", { type: "image/jpeg" }));
        },
        "image/jpeg",
        quality
      );
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(file);
    };
    img.src = url;
  });
}

async function sendRegistration(body: FormData) {
  const res = await fetch(`${API_URL}/api/v1/register`, {
    method: "POST",
    body,
  });

  if (!res.ok) {
    let msg = "No se pudo completar la inscripción. Intenta de nuevo.";
    try {
      const text = await res.text();
      try {
        const j = JSON.parse(text);
        if (typeof j.detail === "string") msg = j.detail;
      } catch {
        if (text) msg = text;
      }
    } catch {}
    throw new Error(msg);
  }
}

function CopyButton({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      type="button"
      onClick={() => {
        void navigator.clipboard?.writeText(text);
        setOk(true);
        setTimeout(() => setOk(false), 1500);
      }}
      className="rounded-full bg-[#f0f4f8] px-3 py-1 text-xs font-semibold text-[#2c4255] transition-transform active:scale-95"
    >
      {ok ? "¡Copiado!" : "Copiar"}
    </button>
  );
}

export default function MultiStepForm() {
  const reduce = useReducedMotion();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const firstRender = useRef(true);

  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<FieldKey, string>>>({});
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [toast, setToast] = useState(false);

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  // Despierta el servidor (Render gratis se duerme) mientras la persona llena el formulario
  useEffect(() => {
    if (PRUEBA) return;
    fetch(`${API_URL}/health`, { cache: "no-store" }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(false), 7000);
    return () => clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  // Al cambiar de paso, deja la tarjeta centrada en pantalla
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    wrapRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
  }, [step, reduce]);

  // Al terminar, lleva la vista al inicio de la confirmación
  useEffect(() => {
    if (done) wrapRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }, [done, reduce]);

  const variants = {
    initial: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * 24, filter: reduce ? "blur(0px)" : "blur(4px)" }),
    animate: { opacity: 1, x: 0, filter: "blur(0px)", transition: { duration: 0.34, ease: EASE } },
    exit: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * -16, filter: reduce ? "blur(0px)" : "blur(4px)", transition: { duration: 0.16, ease: EASE } }),
  };

  function onPickFile(f: File | undefined) {
    setFileError(null);
    setFormError(null);
    if (!f) return;
    if (f.size > 15 * 1024 * 1024) {
      setFileError("La imagen es muy pesada (máx. 15 MB).");
      return;
    }
    setFile(f);
  }

  async function next() {
    const found: Partial<Record<FieldKey, string>> = {};
    for (const f of current.fields) {
      const msg = f.validate(values[f.key]);
      if (msg) found[f.key] = msg;
    }
    setErrors(found);
    setFormError(null);
    if (Object.keys(found).length) return;

    if (current.kind === "pago" && !file) {
      setFileError("Sube el comprobante de pago para continuar.");
      return;
    }

    if (!isLast) {
      setDirection(1);
      setStep((s) => s + 1);
      return;
    }

    unlockAudio();
    setSending(true);
    try {
      if (PRUEBA) {
        await sleep(900);
      } else {
        const body = new FormData();
        Object.entries(values).forEach(([k, v]) => body.append(k, v.trim()));
        const img = await compressImage(file as File);
        body.append("comprobante", img, img.name);
        await sendRegistration(body);
      }
      playSuccessChime();
      setDone(true);
      setToast(true);
    } catch (e: unknown) {
      if (e instanceof TypeError) {
        setFormError("No pudimos conectar con el servidor. Revisa tu conexión e intenta de nuevo.");
      } else {
        setFormError(e instanceof Error ? e.message : "Ocurrió un error. Intenta de nuevo.");
      }
    } finally {
      setSending(false);
    }
  }

  function back() {
    setErrors({});
    setFileError(null);
    setFormError(null);
    setDirection(-1);
    setStep((s) => Math.max(0, s - 1));
  }

  return (
    <div ref={wrapRef} className="scroll-mt-4">
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
                <p className="font-bold text-[#2c4255]">¡Inscripción recibida!</p>
                <p className="mt-0.5 text-sm text-[#5b6e80]">
                  Recibimos tu comprobante. Verificaremos tu pago y te confirmaremos tu lugar.
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
        <RegistrationSuccess
          nombre={values.nombre}
          cedula={values.cedula}
          correo={values.correo}
          institucion={values.institucion}
          prueba={PRUEBA}
        />
      ) : (
        <div className="liquid-glass p-6 sm:p-9">
          {PRUEBA && (
            <p className="mb-5 inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
              Modo prueba · no se guarda ni se envía nada
            </p>
          )}

          <ProgressBar current={step} total={STEPS.length} />

          <div className="flex min-h-[400px] flex-col justify-center">
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
                      autoFocus={step > 0}
                      className="liquid-glass-input"
                      type={f.type ?? "text"}
                      inputMode={f.inputMode}
                      autoComplete={f.autoComplete}
                      autoCapitalize={f.key === "correo" ? "none" : f.key === "nombre" ? "words" : undefined}
                      placeholder={f.placeholder}
                      value={values[f.key]}
                      aria-invalid={errors[f.key] ? true : undefined}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          void next();
                        }
                      }}
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

                {current.kind === "pago" && (
                  <div>
                    <div className="rounded-2xl border border-[#b8d1e1]/70 bg-white/80 text-sm">
                      <p className="eyebrow px-4 pt-3">Pago móvil</p>
                      <div className="divide-y divide-[#b8d1e1]/50">
                        {PAGO.map((p) => (
                          <div key={p.label} className="flex items-center justify-between gap-3 px-4 py-2.5">
                            <div>
                              <p className="text-xs text-[#5b6e80]">{p.label}</p>
                              <p className="font-semibold tabular-nums text-[#2c4255]">{p.value}</p>
                            </div>
                            <CopyButton text={p.copy} />
                          </div>
                        ))}
                      </div>
                    </div>

                    <div
                      role="button"
                      tabIndex={0}
                      onClick={() => fileInputRef.current?.click()}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          fileInputRef.current?.click();
                        }
                      }}
                      className="mt-4 flex cursor-pointer items-center gap-3 rounded-2xl border border-dashed border-[#0088cc]/50 bg-white/70 p-4 transition-colors hover:bg-white focus-within:ring-2 focus-within:ring-[#0088cc]"
                    >
                      {preview ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={preview} alt="Vista previa del comprobante" className="h-14 w-14 shrink-0 rounded-xl object-cover" />
                      ) : (
                        <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-[#f0f4f8] text-[#0088cc]">
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                            <path d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" />
                          </svg>
                        </span>
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate font-semibold text-[#2c4255]">
                          {file ? file.name : "Subir comprobante de pago"}
                        </span>
                        <span className="block text-xs text-[#5b6e80]">
                          {file ? "Toca para cambiar la imagen" : "Foto o captura de pantalla"}
                        </span>
                      </span>
                    </div>

                    <input
                      ref={fileInputRef}
                      id="comprobante"
                      type="file"
                      accept="image/*,image/heic,image/heif"
                      className="hidden"
                      onChange={(e) => onPickFile(e.target.files?.[0])}
                    />

                    <p className="field-message" role="alert">
                      {fileError}
                    </p>
                  </div>
                )}

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
            <button
              type="button"
              onClick={() => void next()}
              className={`glass-button flex-1 ${isLast ? "glass-button-brand shine" : ""}`}
              disabled={sending}
            >
              {sending ? <span className="spinner" /> : isLast ? "Enviar inscripción" : "Continuar"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}