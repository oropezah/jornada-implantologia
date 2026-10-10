export type Speaker = {
    name: string;
    role: string;
    topic: string;
    bio: string;
    highlights: string[];
  };
  
  const base = {
    role: "Especialista en Implantología Bucal",
    topic: "Tema de la ponencia por confirmar",
    bio: "Información del ponente próximamente. Aquí irá su trayectoria, formación y experiencia clínica.",
    highlights: ["Formación académica por confirmar", "Experiencia clínica por confirmar"],
  };
  
  export const SPEAKERS: Speaker[] = [
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
  ].map((name) => ({ name, ...base }));
  
  export function initials(name: string) {
    return name
      .replace(/^(Dr|Dra)\.?\s+/i, "")
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0])
      .join("")
      .toUpperCase();
  }