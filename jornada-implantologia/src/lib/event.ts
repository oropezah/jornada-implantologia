export const EVENT = {
    title: "III Jornada de Actualización en Implantología Bucal",
    short: "III Jornada IBUC 2026",
    place: "Instituto Docente de Urología",
    org: "Universidad de Carabobo · Facultad de Odontología",
    date: new Date("2026-11-21T00:00:00-04:00"),
  };
  
  export const calendarUrl = () =>
    "https://calendar.google.com/calendar/render?action=TEMPLATE" +
    "&text=" + encodeURIComponent(EVENT.title) +
    "&dates=20261121/20261122" +
    "&details=" + encodeURIComponent("Organiza: " + EVENT.org) +
    "&location=" + encodeURIComponent(EVENT.place);
  
  export const mapsUrl = () =>
    "https://www.google.com/maps/search/?api=1&query=" +
    encodeURIComponent(EVENT.place + " Valencia Carabobo Venezuela");