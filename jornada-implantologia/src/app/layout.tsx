import type { Metadata, Viewport } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  display: "swap",
});

export const metadata: Metadata = {
  title: "III Jornada de Actualización en Implantología Bucal · UC",
  description:
    "Inscríbete a la III Jornada de Actualización en Implantología Bucal de la Universidad de Carabobo. 21 de noviembre de 2026, Instituto Docente de Urología.",
  openGraph: {
    title: "III Jornada de Actualización en Implantología Bucal",
    description: "Universidad de Carabobo · 21 de noviembre de 2026. Inscríbete aquí.",
    type: "website",
    locale: "es_VE",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f0f4f8",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={montserrat.variable}>
      <body>{children}</body>
    </html>
  );
}