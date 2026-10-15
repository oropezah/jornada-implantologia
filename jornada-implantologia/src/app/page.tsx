import BackgroundFX from "@/components/BackgroundFX";
import EventCard from "@/components/EventCard";
import MultiStepForm from "@/components/MultiStepForm";
import Reveal from "@/components/Reveal";
import SpeakersSection from "@/components/SpeakersSection";
import TiltCard from "@/components/TiltCard";
import WelcomeSplash from "@/components/WelcomeSplash";

const d = (i: number) => ({ ["--i" as string]: i }) as React.CSSProperties;

export default function Home() {
  return (
    <div className="flex min-h-dvh flex-col">
      <WelcomeSplash />
      <BackgroundFX />

      <main className="flex-1">
        {/* Primera pantalla: título + formulario + evento, centrados */}
        <section className="mx-auto grid min-h-dvh w-full max-w-6xl content-center items-start gap-6 px-5 py-8 sm:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-x-16 lg:gap-y-6">
          <div className="lg:col-start-1 lg:row-start-1 lg:self-end">
            <p className="eyebrow reveal" style={d(0)}>
              Universidad de Carabobo · Facultad de Odontología
            </p>
            <h1 className="display reveal mt-4" style={d(1)}>
              III Jornada de Actualización en Implantología Bucal
            </h1>
            <p className="lead reveal mt-4 max-w-xl" style={d(2)}>
              Asegura tu lugar en menos de un minuto.
            </p>
          </div>

          <div id="inscripcion" className="reveal lg:col-start-2 lg:row-span-2 lg:row-start-1 lg:self-center" style={d(3)}>
            <TiltCard>
              <MultiStepForm />
            </TiltCard>
          </div>

          <div className="reveal lg:col-start-1 lg:row-start-2 lg:self-start" style={d(4)}>
            <EventCard />
          </div>
        </section>

        {/* Ponentes */}
        <section className="mx-auto w-full max-w-6xl px-5 pb-20 pt-4 sm:px-8">
          <Reveal>
            <p className="eyebrow">Programa académico</p>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-[#2c4255] sm:text-3xl">Conoce a los ponentes</h2>
            <p className="lead mt-2 max-w-xl">Especialistas que compartirán lo último en implantología bucal.</p>
          </Reveal>

          <div className="mt-6">
            <SpeakersSection />
          </div>

          <Reveal>
            <p className="mt-8 text-sm text-[#5b6e80]">
              Más información: 0424-4000350 ·{" "}
              <a href="https://instagram.com/implantologiafouc" target="_blank" rel="noopener noreferrer" className="font-semibold text-[#0088cc] underline-offset-4 hover:underline">
                @implantologiafouc
              </a>
            </p>
          </Reveal>
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