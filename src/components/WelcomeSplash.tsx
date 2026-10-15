"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import ImplantLogo from "./ImplantLogo";

const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

const SHAPES = [
  { points: "0,0 20,0 0,34", fill: "#7a8da2", from: { x: -10, y: -10 } },
  { points: "100,0 58,0 100,26", fill: "#b8d1e1", from: { x: 10, y: -10 } },
  { points: "100,30 90,38 100,48", fill: "#7a8da2", from: { x: 10, y: 0 } },
  { points: "100,68 80,86 100,100", fill: "#7a8da2", from: { x: 10, y: 10 } },
  { points: "0,100 0,80 44,100", fill: "#b8d1e1", from: { x: -10, y: 10 } },
];

function Words({ text, start, step = 0.08, y, blur }: { text: string; start: number; step?: number; y: number; blur: string }) {
  return (
    <>
      {text.split(" ").map((w, i) => (
        <motion.span
          key={w + i}
          className="mr-[0.28em] inline-block last:mr-0"
          initial={{ opacity: 0, y, filter: blur }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.7, ease: EASE, delay: start + i * step }}
        >
          {w}
        </motion.span>
      ))}
    </>
  );
}

export default function WelcomeSplash() {
  const reduce = useReducedMotion();
  const [show, setShow] = useState(true);

  useEffect(() => {
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    window.scrollTo({ top: 0, left: 0, behavior: "instant" as ScrollBehavior });
    document.documentElement.dataset.welcome = "pending";
    const t = setTimeout(() => setShow(false), reduce ? 900 : 3600);
    return () => clearTimeout(t);
  }, [reduce]);

  useEffect(() => {
    document.body.style.overflow = show ? "hidden" : "";
    if (!show) {
      window.scrollTo({ top: 0, left: 0, behavior: "instant" as ScrollBehavior });
      document.documentElement.dataset.welcome = "done";
      window.dispatchEvent(new Event("welcome:done"));
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [show]);

  const y = reduce ? 0 : 16;
  const blur = reduce ? "blur(0px)" : "blur(6px)";

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          key="splash"
          onClick={() => setShow(false)}
          className="fixed inset-0 z-[100] cursor-pointer overflow-hidden bg-[#eef3f8]"
          exit={{
            opacity: 0,
            scale: reduce ? 1 : 1.03,
            filter: reduce ? "blur(0px)" : "blur(8px)",
            transition: { duration: 0.6, ease: EASE },
          }}
        >
          {/* Formas angulares del flyer */}
          <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden>
            {SHAPES.map((s, i) => (
              <motion.polygon
                key={i}
                points={s.points}
                fill={s.fill}
                initial={{ opacity: 0, x: reduce ? 0 : s.from.x, y: reduce ? 0 : s.from.y }}
                animate={{ opacity: 0.92, x: 0, y: 0 }}
                transition={{ duration: 1.1, ease: EASE, delay: 0.1 + i * 0.08 }}
              />
            ))}
          </svg>

          {/* Halo suave detrás del contenido */}
          <motion.div
            aria-hidden
            className="absolute left-1/2 top-1/2 h-[70vmin] w-[70vmin] -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{ background: "radial-gradient(circle, rgba(255,255,255,0.9), rgba(255,255,255,0) 70%)" }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.4, ease: EASE }}
          />

          <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
            <motion.p
              className="text-[0.7rem] font-bold uppercase leading-snug tracking-[0.18em] text-[#1e2e3d] sm:text-sm"
              initial={{ opacity: 0, y }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 0.2 }}
            >
              Universidad de Carabobo
              <br />
              Facultad de Odontología
            </motion.p>

            <div className="mt-8 flex flex-col items-center gap-6 md:flex-row md:gap-9">
              <div className="flex items-stretch gap-3">
                <ImplantLogo className="h-28 w-auto md:h-52" delay={0.3} />
                <motion.span
                  className="hidden text-[0.62rem] font-semibold uppercase tracking-[0.2em] text-[#2c4255] md:block [writing-mode:vertical-rl] rotate-180"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.8, delay: 1.2 }}
                >
                  III Jornada <span className="text-[#0088cc]">IBUC 2026</span>
                </motion.span>
              </div>

              <div className="text-center md:text-left">
                <h1>
                  <span className="block text-[2.6rem] font-light leading-none tracking-wide text-[#0088cc] sm:text-6xl md:text-7xl">
                    <Words text="III JORNADA" start={0.7} y={y} blur={blur} />
                  </span>
                  <span className="mt-3 block text-[1.1rem] font-extrabold uppercase leading-tight tracking-[0.2em] text-[#2c4255] sm:text-3xl md:text-4xl">
                    <span className="block">
                      <Words text="ACTUALIZACIÓN EN" start={1.0} y={y} blur={blur} />
                    </span>
                    <span className="block">
                      <Words text="IMPLANTOLOGÍA BUCAL" start={1.3} y={y} blur={blur} />
                    </span>
                  </span>
                </h1>
                <motion.p
                  className="mx-auto mt-4 max-w-md text-sm text-[#2c4255]/80 md:mx-0 md:text-base"
                  initial={{ opacity: 0, y }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.7, ease: EASE, delay: 1.7 }}
                >
                  Del programa de Especialización en Implantología Bucal de la Universidad de Carabobo
                </motion.p>
              </div>
            </div>

            <motion.div
              className="mt-8 flex items-center gap-3 text-left"
              initial={{ opacity: 0, y }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 2.0 }}
            >
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#5b6e80" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <path d="M12 21s7-6.2 7-11.5A7 7 0 005 9.5C5 14.8 12 21 12 21z" />
                <circle cx="12" cy="9.5" r="2.6" />
              </svg>
              <div>
                <p className="text-lg font-bold uppercase tracking-wide text-[#0088cc] sm:text-xl">21 de noviembre 2026</p>
                <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#2c4255] sm:text-sm">Instituto Docente de Urología</p>
              </div>
            </motion.div>

            <motion.div
              className="mt-8 h-[3px] w-24 origin-left rounded-full bg-gradient-to-r from-[#0088cc] to-[#4cc3ff]"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.8, ease: EASE, delay: 2.3 }}
            />
            <motion.p
              className="mt-3 text-[0.7rem] font-medium text-[#5b6e80]"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 2.6 }}
            >
              Toca para continuar
            </motion.p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}