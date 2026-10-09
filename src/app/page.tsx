import MultiStepForm from "@/components/MultiStepForm";

const SPEAKERS = [
  "Dr. Marco Rodríguez",
  "Dr. José Ramón Russian",
  "Dra. Dubraska Valverde",
  "Dr. Ricardo Brito",
  "Dr. Luis Alberto García",
  "Dra. Clelia Ferreira",
  "Dr. Rodrigo Pino",
  "Dr. Braulio López",
  "Dra. Adriana Borjas",
  "Dra. María Laura Ramírez",
];

export default function Home() {
  return (
    <div className="flex min-h-dvh flex-col">
      <main className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:gap-16 lg:py-16">
        {/* Información */}
        <section>
          <p className="eyebrow reveal" style={{ ["--i" as string]: 0 } as React.CSSProperties}>
            Universidad de Carabobo · Facultad de Odontología
          </p>

          <h1
            className="display reveal mt-4"
            style={{ ["--i" as string]: 1 } as React.CSSProperties}
          >
            III Jornada de Actualización en Implantología Bucal
          </h1>

          <p
            className="lead reveal mt-4 max-w-xl"
            style={{ ["--i" as string]: 2 } as React.CSSProperties}
          >
            Una jornada para actualizarte con especialistas. Asegura tu lugar en menos de un minuto.
          </p>

          <div
            className="reveal mt-6 flex flex-wrap gap-2.5"
            style={{ ["--i" as string]: 3 } as React.CSSProperties}
          >
            <span className="chip">📅 21 de noviembre, 2026</span>
            <span className="chip">📍 Instituto Docente de Urología</span>
          </div>

          <div
            className="reveal mt-9"
            style={{ ["--i" as string]: 4 } as React.CSSProperties}
          >
            <p className="eyebrow mb-3">Ponentes</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {SPEAKERS.map((name) => (
                <div key={name} className="speaker">
                  {name}
                </div>
              ))}
            </div>
          </div>

          <p
            className="reveal mt-6 text-sm text-[#5b6e80]"
            style={{ ["--i" as string]: 5 } as React.CSSProperties}
          >
            Más información: 0424-4000350 ·{" "}
            <a
              href="https://instagram.com/implantologiafouc"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-[#0088cc] underline-offset-4 hover:underline"
            >
              @implantologiafouc
            </a>
          </p>
        </section>

        {/* Formulario */}
        <section
          className="reveal"
          style={{ ["--i" as string]: 3 } as React.CSSProperties}
          aria-label="Formulario de inscripción"
        >
          <MultiStepForm />
        </section>
      </main>

      <footer className="px-5 pb-8 pt-2 text-center text-sm text-[#5b6e80]">
        Creado por{" "}
        <a
          href="https://instagram.com/synco.ia"
          target="_blank"
          rel="noopener noreferrer"
          className="font-semibold text-[#2c4255] underline-offset-4 transition-colors hover:text-[#0088cc] hover:underline"
        >
          Synco
        </a>
      </footer>
    </div>
  );
}