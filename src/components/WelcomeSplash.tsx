"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

const EASE = [0.23, 1, 0.32, 1] as const;
const WORDS = ["III", "Jornada", "de", "Actualización", "en", "Implantología", "Bucal"];

export default function WelcomeSplash() {
  const reduce = useReducedMotion();
  const [show, setShow] = useState(true);

  useEffect(() => {
    document.documentElement.dataset.welcome = "pending";
    const t = setTimeout(() => setShow(false), reduce ? 900 : 3200);
    return () => clearTimeout(t);
  }, [reduce]);

  useEffect(() => {
    document.body.style.overflow = show ? "hidden" : "";
    if (!show) document.documentElement.dataset.welcome = "done";
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
          className="fixed inset-0 z-[100] grid cursor-pointer place-items-center overflow-hidden px-6 text-center"
          style={{
            background:
              "radial-gradient(60% 45% at 50% 30%, rgba(0,136,204,0.18), transparent 70%), linear-gradient(180deg, #eaf1f7, #f0f4f8)",
          }}
          exit={{
            opacity: 0,
            scale: reduce ? 1 : 1.03,
            filter: reduce ? "blur(0px)" : "blur(8px)",
            transition: { duration: 0.6, ease: EASE },
          }}
        >
          <div className="max-w-3xl">
            <motion.p
              className="eyebrow"
              initial={{ opacity: 0, y }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 0.2 }}
            >
              Bienvenido a la
            </motion.p>

            <h1 className="mt-5 flex flex-wrap justify-center gap-x-[0.28em] text-[2.1rem] font-bold leading-[1.05] tracking-tight text-[#2c4255] sm:text-5xl lg:text-6xl">
              {WORDS.map((w, i) => (
                <motion.span
                  key={w + i}
                  className="inline-block"
                  initial={{ opacity: 0, y, filter: blur }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  transition={{ duration: 0.7, ease: EASE, delay: 0.7 + i * 0.09 }}
                >
                  {w}
                </motion.span>
              ))}
            </h1>

            <motion.div
              className="mx-auto mt-8 h-[3px] w-24 origin-left rounded-full bg-gradient-to-r from-[#0088cc] to-[#4cc3ff]"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.8, ease: EASE, delay: 1.7 }}
            />

            <motion.p
              className="mt-5 text-sm font-medium text-[#5b6e80]"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 2.0 }}
            >
              21 de noviembre, 2026 · Universidad de Carabobo
            </motion.p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}