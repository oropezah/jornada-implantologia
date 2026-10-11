"use client";

import { motion } from "framer-motion";

const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

const CHAT = [
  { who: "p", text: "Hola, ¿tienen cita para limpieza esta semana?" },
  { who: "b", text: "¡Hola! Tengo mañana 10:00 am o jueves 3:30 pm. ¿Cuál prefieres?" },
  { who: "p", text: "Mañana a las 10." },
  { who: "b", text: "Listo, tu cita quedó agendada ✓ Te la recuerdo un día antes." },
];

export default function SyncoPitch() {
  return (
    <div className="rounded-2xl border border-[#b8d1e1]/70 bg-gradient-to-br from-white/90 to-[#e6f2fb]/90 p-5">
      <p className="eyebrow">Hecho por Synco</p>
      <h4 className="mt-2 text-lg font-bold leading-snug tracking-tight text-[#2c4255]">
        Esta inscripción se hizo sola. Tu consultorio también puede.
      </h4>
      <p className="mt-1.5 text-sm text-[#5b6e80]">
        Creamos chatbots con IA para WhatsApp que responden a tus pacientes, agendan citas y confirman asistencia las 24 horas.
      </p>

      <div className="mt-4 space-y-2 rounded-xl bg-[#eaf1f7]/80 p-3">
        {CHAT.map((m, i) => (
          <motion.div
            key={i}
            className={m.who === "b" ? "flex justify-end" : "flex justify-start"}
            initial={{ opacity: 0, y: 10, scale: 0.96 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: "-20px" }}
            transition={{ duration: 0.4, ease: EASE, delay: 0.4 + i * 0.9 }}
          >
            <span
              className={
                m.who === "b"
                  ? "max-w-[82%] rounded-2xl rounded-br-sm bg-[#0088cc] px-3 py-2 text-[0.8rem] leading-snug text-white"
                  : "max-w-[82%] rounded-2xl rounded-bl-sm bg-white px-3 py-2 text-[0.8rem] leading-snug text-[#2c4255] shadow-sm"
              }
            >
              {m.text}
            </span>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <a
          href="https://synco-agency.com"
          target="_blank"
          rel="noopener noreferrer"
          className="shine inline-flex items-center rounded-full bg-[#2c4255] px-4 py-2 text-sm font-semibold text-white transition-transform duration-200 active:scale-95"
        >
          Conocer Synco
        </a>
        <a
          href="https://instagram.com/synco.ia"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-semibold text-[#0088cc] underline-offset-4 hover:underline"
        >
          @synco.ia
        </a>
      </div>
    </div>
  );
}