import MultiStepForm from "@/components/MultiStepForm";
import SpeakersSection from "@/components/SpeakersSection";
import WelcomeSplash from "@/components/WelcomeSplash";

const d = (i: number) => ({ ["--i" as string]: i }) as React.CSSProperties;

export default function Home() {
  return (
    <div className="flex min-h-dvh flex-col">
      <WelcomeSplash />

      <main className="mx-auto grid w-full max-w-6xl flex-1 items-start gap-10 px-5 py-8 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:gap-x-16 lg:gap-y-10 lg:py-16">
        {/* 1. Intro */}
        <section className="lg:col-start-1 lg:row-start-1">
          <p className="eyebrow reveal" style={d(0)}>
            Universidad de Carabobo · Facultad de Odontología
          </p>
          <h1 className="display reveal mt-4" style={d(1)}>
            III Jornada de Actualización en Implantología Bucal
          </h1>
          <p className="lead reveal mt-4 max-w-xl" style={d(2)}>
            Asegura tu lugar en menos de un minuto.
          </p>
          <div className="reveal mt-6 flex flex-wrap gap-2.5" style={d(3)}>
            <span className="chip">📅 21 de noviembre, 2026</span>
            <span className="chip">📍 Instituto Docente de Urología</span>
          </div>
        </section>

        {/* 2. Formulario (en móvil queda justo después del título) */}
        <section
          className="reveal lg:sticky lg:top-10 lg:col-start-2 lg:row-span-2 lg:row-start-1"
          style={d(4)}
          aria-label="Formulario de inscripción"
        >
          <MultiStepForm />
        </section>

        {/* 3. Ponentes */}
        <section className="reveal lg:col-start-1 lg:row-start-2" style={d(5)}>
          <SpeakersSection />
          <p className="mt-6 text-sm text-[#5b6e80]">
            Más información: 0424-4000350 ·{" "}
            <a href="https://instagram.com/implantologiafouc" target="_blank" rel="noopener noreferrer" className="font-semibold text-[#0088cc] underline-offset-4 hover:underline">
              @implantologiafouc
            </a>
          </p>
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
        </a>{" "}
        · @synco.ia
      </footer>
    </div>
  );
}