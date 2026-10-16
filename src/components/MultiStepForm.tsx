"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import ProgressBar from "./ProgressBar";
import RegistrationSuccess from "./RegistrationSuccess";
import { playSuccessChime, unlockAudio } from "@/lib/sound";

const PRUEBA = false;

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "https://jornada-implantologia.onrender.com").replace(/\/$/, "");
const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

const PAGO_MOBILE = [
  { label: "Cédula", value: "27.381.498", copy: "27381498" },
  { label: "Teléfono", value: "04244240537", copy: "04244240537" },
  { label: "Banco", value: "Banco de Venezuela", copy: "Banco de Venezuela" },
];

const PAGO_BINANCE = [
  { label: "Correo / Pay ID", value: "ana.rangel262@gmail.com", copy: "ana.rangel262@gmail.com" },
  { label: "Moneda", value: "USDT", copy: "USDT" },
];

type FieldKey = "nombre" | "cedula" | "correo" | "telefono" | "institucion";

type FieldDef = {
  key: FieldKey;
  label: string;
  placeholder: string;
  type?: string;
  inputMode?: "text" | "numeric" | "tel" | "email";
  autoComplete?: string;
  kind?: "text" | "select";
  options?: { label: string; value: string }[];
  validate: (v: string) => string | null;
};

type Step = { title: string; hint: string; fields: FieldDef[]; kind?: "pago" };

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
    title: "Selecciona tu condición",
    hint: "Indica si eres estudiante, odontólogo general o especialista.",
    fields: [
      {
        key: "institucion",
        label: "Condición",
        placeholder: "Selecciona una opción",
        kind: "select",
        options: [
          { label: "Estudiante (€80)", value: "Estudiante" },
          { label: "Odontólogo General (€100)", value: "Odontólogo General" },
          { label: "Especialista (€120)", value: "Especialista" },
        ],
        validate: (v) => (!v.trim() ? "Selecciona tu condición para determinar la tarifa." : null),
      },
    ],
  },
  {
    title: "Realiza tu pago",
    hint: "Selecciona el método de tu preferencia.",
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
      className="rounded-full bg-[#f0f4f8] px-2.5 py-0.5 text-xs font-semibold text-[#2c4255] transition-transform active:scale-95"
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

  // Estado para la Tasa del Euro (BCV)
  const [eurRate, setEurRate] = useState<number>(980.61);
  const [method, setMethod] = useState<"pago_movil" | "binance" | "efectivo">("pago_movil");

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  // Consulta Tasa Euro BCV
  useEffect(() => {
    async function fetchRate() {
      try {
        const res = await fetch("https://ve.dolarapi.com/v1/cotizaciones");
        if (res.ok) {
          const data = await res.json();
          const eur = data.find((item: { moneda: string }) => item.moneda === "EUR");
          if (eur?.promedio) {
            setEurRate(eur.promedio);
          }
        }
      } catch (e) {
        console.warn("Error al cargar la tasa del euro:", e);
      }
    }
    fetchRate();
  }, []);

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

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    wrapRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
  }, [step, reduce]);

  useEffect(() => {
    if (done) wrapRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }, [done, reduce]);

  const variants = {
    initial: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * 20, filter: reduce ? "blur(0px)" : "blur(3px)" }),
    animate: { opacity: 1, x: 0, filter: "blur(0px)", transition: { duration: 0.3, ease: EASE } },
    exit: (d: number) => ({ opacity: 0, x: reduce ? 0 : d * -12, filter: reduce ? "blur(0px)" : "blur(3px)", transition: { duration: 0.15, ease: EASE } }),
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

    if (current.kind === "pago" && !file && method !== "efectivo") {
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
        body.append("metodo_pago", method);
        if (file) {
          const img = await compressImage(file as File);
          body.append("comprobante", img, img.name);
        }
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

  // Precios dinámicos
  let eurAmount = 120; // Tarifa por defecto
  if (values.institucion === "Estudiante") {
    eurAmount = 80;
  } else if (values.institucion === "Odontólogo General") {
    eurAmount = 100;
  } else if (values.institucion === "Especialista") {
    eurAmount = 120;
  }

  const bsAmount = (eurAmount * eurRate).toLocaleString("es-VE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const whatsappMessage = encodeURIComponent(
    `¡Hola! Quisiera registrarme y coordinar mi pago en efectivo para la jornada.\n\n` +
      `*Nombre:* ${values.nombre || "No especificado"}\n` +
      `*Cédula:* ${values.cedula || "No especificada"}\n` +
      `*Condición:* ${values.institucion || "No especificada"} (€${eurAmount})\n` +
      `*Teléfono:* ${values.telefono || "No especificado"}`
  );

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
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-[#0088cc] to-[#12b886] text-white">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <polyline points="5 12.5 10 17.5 19 7.5" />
                </svg>
              </span>
              <div className="flex-1">
                <p className="font-bold text-[#2c4255]">¡Inscripción recibida!</p>
                <p className="mt-0.5 text-xs text-[#5b6e80]">
                  Recibimos tus datos. Nos pondremos en contacto contigo para confirmar tu lugar.
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
        <div className="liquid-glass p-5 sm:p-7">
          {PRUEBA && (
            <p className="mb-3 inline-flex rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800">
              Modo prueba · no se guarda ni se envía nada
            </p>
          )}

          <ProgressBar current={step} total={STEPS.length} />

          <div className="flex min-h-[200px] flex-col justify-center py-2">
            <AnimatePresence mode="wait" custom={direction} initial={false}>
              <motion.div key={step} custom={direction} variants={variants} initial="initial" animate="animate" exit="exit">
                <h3 className="text-xl font-bold tracking-tight text-[#2c4255] sm:text-[1.35rem]">{current.title}</h3>
                <p className="mb-4 mt-0.5 text-xs text-[#5b6e80] sm:text-sm">{current.hint}</p>

                {current.fields.map((f) => (
                  <div key={f.key}>
                    {f.kind === "select" ? (
                      <select
                        id={f.key}
                        name={f.key}
                        aria-label={f.label}
                        className="liquid-glass-input cursor-pointer"
                        value={values[f.key]}
                        aria-invalid={errors[f.key] ? true : undefined}
                        onChange={(e) => {
                          setValues((v) => ({ ...v, [f.key]: e.target.value }));
                          if (errors[f.key]) setErrors((er) => ({ ...er, [f.key]: undefined }));
                        }}
                      >
                        <option value="" disabled>
                          {f.placeholder}
                        </option>
                        {f.options?.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    ) : (
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
                    )}
                    <p className="field-message" role="alert">
                      {errors[f.key]}
                    </p>
                  </div>
                ))}

                {current.kind === "pago" && (
                  <div>
                    {/* Selector de Método de Pago */}
                    <div className="mb-3 grid grid-cols-3 gap-1.5 sm:gap-2">
                      <button
                        type="button"
                        onClick={() => setMethod("pago_movil")}
                        className={`rounded-xl p-2 sm:p-2.5 text-center text-[0.72rem] sm:text-xs font-bold transition-all ${
                          method === "pago_movil"
                            ? "bg-[#0088cc] text-white shadow-md"
                            : "bg-white/70 text-[#2c4255] hover:bg-white"
                        }`}
                      >
                        Pago Móvil
                      </button>
                      <button
                        type="button"
                        onClick={() => setMethod("binance")}
                        className={`rounded-xl p-2 sm:p-2.5 text-center text-[0.72rem] sm:text-xs font-bold transition-all ${
                          method === "binance"
                            ? "bg-[#0088cc] text-white shadow-md"
                            : "bg-white/70 text-[#2c4255] hover:bg-white"
                        }`}
                      >
                        Binance Pay
                      </button>
                      <button
                        type="button"
                        onClick={() => setMethod("efectivo")}
                        className={`rounded-xl p-2 sm:p-2.5 text-center text-[0.72rem] sm:text-xs font-bold transition-all ${
                          method === "efectivo"
                            ? "bg-[#0088cc] text-white shadow-md"
                            : "bg-white/70 text-[#2c4255] hover:bg-white"
                        }`}
                      >
                        Efectivo
                      </button>
                    </div>

                    {/* Detalle de Pago según método */}
                    {method === "efectivo" ? (
                      <div className="rounded-xl border border-[#b8d1e1]/70 bg-white/80 p-3.5 text-xs sm:text-sm space-y-3">
                        <div className="flex items-center justify-between border-b border-[#b8d1e1]/40 pb-2">
                          <span className="eyebrow text-[0.7rem]">Pago en Efectivo</span>
                          <span className="font-extrabold text-[#0088cc] text-sm sm:text-base">
                            €{eurAmount} / ${eurAmount}
                          </span>
                        </div>
                        <p className="text-[#5b6e80] text-xs leading-relaxed">
                          Puedes realizar tu pago directamente en efectivo. Haz clic abajo para coordinar la entrega con nosotros por WhatsApp.
                        </p>
                        <a
                          href={`https://wa.me/584244000350?text=${whatsappMessage}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-center gap-2 rounded-xl bg-[#25D366] px-4 py-2.5 text-xs font-bold text-white shadow-md transition-transform active:scale-95 hover:bg-[#20bd5a]"
                        >
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                            <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-1.156 4.22 4.22-1.107z" />
                          </svg>
                          Coordinar pago por WhatsApp (0424-4000350)
                        </a>
                      </div>
                    ) : (
                      <div className="rounded-xl border border-[#b8d1e1]/70 bg-white/80 text-xs sm:text-sm">
                        <div className="flex items-center justify-between px-3.5 pt-3 pb-2 border-b border-[#b8d1e1]/40">
                          <span className="eyebrow text-[0.7rem]">
                            {method === "pago_movil" ? "Pago Móvil / Transferencia" : "Binance Pay"}
                          </span>
                          <span className="font-extrabold text-[#0088cc] text-sm sm:text-base">
                            {method === "pago_movil" ? `Bs. ${bsAmount}` : `${eurAmount} USDT`}
                          </span>
                        </div>

                        {method === "pago_movil" && (
                          <p className="px-3.5 pt-2 text-[0.68rem] text-[#5b6e80]">
                            Monto en Bs. calculado a Tasa Euro BCV ({eurRate.toFixed(2)} Bs/EUR) para tarifa de <b>{values.institucion}</b> (€{eurAmount}).
                          </p>
                        )}

                        <div className="divide-y divide-[#b8d1e1]/50">
                          {(method === "pago_movil" ? PAGO_MOBILE : PAGO_BINANCE).map((p) => (
                            <div key={p.label} className="flex items-center justify-between gap-3 px-3.5 py-2">
                              <div>
                                <p className="text-[0.7rem] text-[#5b6e80]">{p.label}</p>
                                <p className="font-semibold tabular-nums text-[#2c4255]">{p.value}</p>
                              </div>
                              <CopyButton text={p.copy} />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Zona de Subida de Comprobante (opcional si es en efectivo) */}
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
                      className="mt-3 flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-[#0088cc]/50 bg-white/70 p-3 transition-colors hover:bg-white focus-within:ring-2 focus-within:ring-[#0088cc]"
                    >
                      {preview ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={preview} alt="Vista previa del comprobante" className="h-11 w-11 shrink-0 rounded-lg object-cover" />
                      ) : (
                        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-[#f0f4f8] text-[#0088cc]">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                            <path d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" />
                          </svg>
                        </span>
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-xs font-semibold text-[#2c4255] sm:text-sm">
                          {file
                            ? file.name
                            : method === "efectivo"
                            ? "Subir comprobante / acuse (opcional)"
                            : "Subir comprobante de pago"}
                        </span>
                        <span className="block text-[0.7rem] text-[#5b6e80]">
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

          <div className="mt-3 flex gap-2.5">
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