let ctx: AudioContext | null = null;
type WebkitWindow = Window & { webkitAudioContext?: typeof AudioContext };

function getCtx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!ctx) {
    const Ctor = window.AudioContext ?? (window as WebkitWindow).webkitAudioContext;
    if (!Ctor) return null;
    ctx = new Ctor();
  }
  return ctx;
}

/** Llamar dentro del click del usuario (Safari/iOS lo exige). */
export function unlockAudio() {
  const c = getCtx();
  if (c && c.state === "suspended") void c.resume();
}

/** Campanita de 3 notas: "¡agendado!" */
export function playSuccessChime() {
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();
  const t0 = c.currentTime + 0.02;
  [
    { f: 783.99, t: 0 },
    { f: 987.77, t: 0.11 },
    { f: 1318.51, t: 0.22 },
  ].forEach(({ f, t }) => {
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = "sine";
    osc.frequency.value = f;
    gain.gain.setValueAtTime(0.0001, t0 + t);
    gain.gain.exponentialRampToValueAtTime(0.22, t0 + t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + t + 0.9);
    osc.connect(gain).connect(c.destination);
    osc.start(t0 + t);
    osc.stop(t0 + t + 1);
  });
}