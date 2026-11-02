"""Emails con Resend: aviso al estudio (diseño portado de n8n) + confirmación al cliente con .ics."""

import base64
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx

from . import config

log = logging.getLogger("mocca.email")
TZ = ZoneInfo(config.TIMEZONE)

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Paleta Mocca
DARK, CREAM, SAND, GOLD, BROWN, TEXT, LINE = "#2B1B17", "#F2EADF", "#EAE1D3", "#C5A059", "#8C6D58", "#5D4D43", "#E6DCCD"
FONT = "'Montserrat',Helvetica,Arial,sans-serif"


@dataclass
class ItemView:
    staff: str
    servicio: str
    minutos: int
    start: datetime
    end: datetime
    auto: bool = False


@dataclass
class CitaView:
    id: int
    nombre: str
    telefono: str
    email: str | None
    fecha: date
    horario: str
    is_express: bool
    fecha_nacimiento: str = ""
    items: list[ItemView] = field(default_factory=list)

    @property
    def first_name(self) -> str:
        return (self.nombre.strip().split(" ") or [""])[0]

    @property
    def servicios_texto(self) -> str:
        return " · ".join(dict.fromkeys(i.servicio for i in self.items))

    @property
    def con_texto(self) -> str:
        return " y ".join(dict.fromkeys(i.staff for i in self.items))


# ── Helpers ──────────────────────────────────────────────────────────────────
def fecha_larga(d: date) -> str:
    return f"{DIAS[d.weekday()].capitalize()} {d.day} de {MESES[d.month - 1]} de {d.year}"


def wa_number(phone: str) -> str:
    """04121234567 → 584121234567 (wa.me exige código de país, sin 0 inicial)."""
    d = re.sub(r"\D", "", phone)
    if d.startswith("00"):
        d = d[2:]
    if d.startswith("0"):
        d = "58" + d[1:]
    elif len(d) == 10:
        d = "58" + d
    return d


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=TZ).astimezone(timezone.utc)


def _span(v: CitaView) -> tuple[datetime, datetime]:
    return min(i.start for i in v.items), max(i.end for i in v.items)


def google_calendar_link(v: CitaView) -> str:
    start, end = _span(v)
    fmt = "%Y%m%dT%H%M%SZ"
    params = {
        "action": "TEMPLATE",
        "text": f"{v.servicios_texto} · {config.STUDIO_NAME}",
        "dates": f"{_utc(start).strftime(fmt)}/{_utc(end).strftime(fmt)}",
        "details": f"Tu cita en {config.STUDIO_NAME} con {v.con_texto}.\nSi no puedes asistir, avísanos con 24 h de anticipación.",
        "location": config.STUDIO_LOCATION,
    }
    return "https://calendar.google.com/calendar/render?" + "&".join(f"{k}={quote(str(val), safe='')}" for k, val in params.items())


def build_ics(v: CitaView) -> str:
    start, end = _span(v)
    fmt = "%Y%m%dT%H%M%SZ"

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mocca Beauty Studio//Reservas//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:cita-{v.id}@mocca-beauty-studio",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime(fmt)}",
        f"DTSTART:{_utc(start).strftime(fmt)}",
        f"DTEND:{_utc(end).strftime(fmt)}",
        f"SUMMARY:{esc(v.servicios_texto + ' · ' + config.STUDIO_NAME)}",
        f"DESCRIPTION:{esc('Cita con ' + v.con_texto + '. Si no puedes asistir, avísanos con 24 h de anticipación.')}",
        f"LOCATION:{esc(config.STUDIO_LOCATION)}",
        "BEGIN:VALARM",
        "TRIGGER:-PT2H",
        "ACTION:DISPLAY",
        "DESCRIPTION:Tu cita en Mocca es en 2 horas",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"


# ── Plantillas ───────────────────────────────────────────────────────────────
def _shell(badge: str, body: str, footer_extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
@media screen and (max-width:600px){{.box{{width:100%!important}}.pad{{padding-left:20px!important;padding-right:20px!important}}}}</style></head>
<body style="margin:0;padding:0;background:{CREAM};font-family:{FONT};">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CREAM};"><tr><td align="center" style="padding:30px 10px;">
<table class="box" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #E2D5C3;">
<tr><td align="center" style="background:{DARK};padding:34px 20px;"><p style="margin:0;color:{CREAM};font-size:20px;font-weight:700;letter-spacing:2px;font-family:{FONT};">MOCCA BEAUTY STUDIO</p></td></tr>
<tr><td align="center" style="padding:24px 20px 0;"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="border:1px solid {GOLD};border-radius:20px;padding:7px 18px;">
<span style="font-size:11px;font-weight:600;color:{BROWN};letter-spacing:2px;text-transform:uppercase;font-family:{FONT};">{badge}</span></td></tr></table></td></tr>
{body}
<tr><td align="center" style="background:{SAND};padding:22px 20px;border-top:1px solid #DFD5C5;">
<p style="margin:0 0 6px;font-weight:700;color:{DARK};font-size:14px;font-family:{FONT};">Mocca Beauty Studio</p>
{footer_extra}
<p style="margin:0;font-size:11px;color:#7A695D;font-family:{FONT};">&copy; {datetime.now().year} Mocca Beauty Studio · Valencia, Venezuela</p></td></tr>
</table></td></tr></table></body></html>"""


def _kv(label: str, value: str, last: bool = False) -> str:
    border = "" if last else f"border-bottom:1px solid {LINE};"
    return (
        f'<tr><td style="padding:14px 0;{border}"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="font-size:11px;text-transform:uppercase;color:{BROWN};font-weight:700;letter-spacing:1.6px;font-family:{FONT};">{label}</td>'
        f'<td align="right" style="font-size:15px;font-weight:600;color:{DARK};font-family:{FONT};">{value}</td></tr></table></td></tr>'
    )


def _button(href: str, text: str, bg: str = DARK, color: str = "#fff") -> str:
    return (
        f'<table cellpadding="0" cellspacing="0" border="0" style="margin:6px auto;"><tr><td style="background:{bg};border-radius:10px;">'
        f'<a href="{escape(href, quote=True)}" target="_blank" style="display:inline-block;padding:15px 30px;font-size:14px;color:{color};'
        f'font-weight:700;text-decoration:none;letter-spacing:.4px;font-family:{FONT};">{text}</a></td></tr></table>'
    )


def studio_email(v: CitaView) -> tuple[str, str]:
    tag = " · Express" if v.is_express else ""
    subject = f"Nueva cita{tag} | {v.nombre} | {DIAS[v.fecha.weekday()].capitalize()} {v.fecha.day}/{v.fecha.month} {v.horario}"

    blocks = ""
    for i in v.items:
        auto = " (asignada automáticamente)" if i.auto else ""
        blocks += (
            f'<tr><td style="padding:14px 0;border-bottom:1px solid {LINE};">'
            f'<p style="margin:0 0 8px;font-size:12px;font-weight:700;color:{BROWN};text-transform:uppercase;letter-spacing:1.6px;font-family:{FONT};">{escape(i.staff)}{escape(auto)}</p>'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:{FONT};">'
            f'<tr><td style="font-size:13px;color:{TEXT};padding:3px 0;">Servicio</td><td align="right" style="font-size:14px;font-weight:600;color:{DARK};">{escape(i.servicio)}</td></tr>'
            f'<tr><td style="font-size:13px;color:{TEXT};padding:3px 0;">Duración</td><td align="right" style="font-size:13px;color:{DARK};">{i.minutos} min</td></tr>'
            f"</table></td></tr>"
        )

    contact = f'<tr><td style="padding:14px 0;border-bottom:1px solid {LINE};font-family:{FONT};font-size:13px;color:{TEXT};line-height:22px;">'
    contact += f"<b style='color:{DARK};'>{escape(v.nombre)}</b><br>Tel: {escape(v.telefono)}"
    if v.email:
        contact += f"<br>Email: {escape(v.email)}"
    if v.fecha_nacimiento:
        contact += f"<br>Nacimiento: {escape(v.fecha_nacimiento)}"
    contact += "</td></tr>"

    body = f"""
<tr><td class="pad" style="padding:26px 40px 14px;">
<h2 style="margin:0 0 10px;font-size:24px;color:{DARK};font-family:{FONT};">Nueva cita, {escape(v.first_name)}</h2>
<p style="margin:0;font-size:15px;line-height:22px;color:{TEXT};font-family:{FONT};">Se registró una nueva cita. Ya está en el calendario de la manicurista.</p></td></tr>
<tr><td class="pad" style="padding:4px 40px 8px;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {LINE};">
{_kv("Fecha", escape(fecha_larga(v.fecha)))}{_kv("Horario", escape(v.horario))}{contact}{blocks}</table></td></tr>
<tr><td class="pad" style="padding:10px 40px 24px;"><div style="background:#F4ECE1;border-left:3px solid {GOLD};padding:16px 18px;border-radius:0 8px 8px 0;">
<p style="margin:0;font-weight:700;font-size:13px;color:{DARK};font-family:{FONT};">Checklist para la asistente</p>
<ul style="margin:8px 0 0;padding-left:18px;color:{TEXT};font-size:13px;line-height:20px;font-family:{FONT};">
<li>Preparar la(s) estación(es) antes de las {escape(v.horario)}.</li><li>Cambios o cancelaciones: con al menos 24 h de anticipación.</li></ul></div></td></tr>
<tr><td align="center" class="pad" style="padding:0 40px 34px;">{_button("https://wa.me/" + wa_number(v.telefono), "Escribir al cliente por WhatsApp", "#25D366")}</td></tr>"""
    badge = "Cita confirmada · Servicio Express" if v.is_express else "Cita confirmada"
    return subject, _shell(badge, body)


def client_email(v: CitaView) -> tuple[str, str]:
    subject = f"Tu cita en Mocca está confirmada · {DIAS[v.fecha.weekday()].capitalize()} {v.fecha.day} de {MESES[v.fecha.month - 1]}, {v.horario}"
    express_note = (
        f'<p style="margin:12px 0 0;font-size:13px;color:{TEXT};font-family:{FONT};">Servicio Express: te atienden manos y pies al mismo tiempo, dos profesionales.</p>'
        if v.is_express
        else ""
    )
    body = f"""
<tr><td class="pad" style="padding:26px 40px 14px;">
<h2 style="margin:0 0 10px;font-size:26px;color:{DARK};font-family:{FONT};">¡Te esperamos, {escape(v.first_name)}!</h2>
<p style="margin:0;font-size:15px;line-height:23px;color:{TEXT};font-family:{FONT};">Tu cita quedó confirmada. Estos son los detalles:</p>{express_note}</td></tr>
<tr><td class="pad" style="padding:4px 40px 8px;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {LINE};">
{_kv("Fecha", escape(fecha_larga(v.fecha)))}{_kv("Hora", escape(v.horario))}{_kv("Servicio", escape(v.servicios_texto))}{_kv("Con", escape(v.con_texto), last=True)}
</table></td></tr>
<tr><td align="center" class="pad" style="padding:22px 40px 6px;">
{_button(google_calendar_link(v), "Agregar a Google Calendar")}
<p style="margin:10px 0 0;font-size:12px;color:#7A695D;font-family:{FONT};">También adjuntamos el archivo .ics para Apple Calendar u Outlook.</p></td></tr>
<tr><td class="pad" style="padding:22px 40px 10px;"><div style="background:#F4ECE1;border-left:3px solid {GOLD};padding:16px 18px;border-radius:0 8px 8px 0;">
<ul style="margin:0;padding-left:18px;color:{TEXT};font-size:13px;line-height:21px;font-family:{FONT};">
<li>Si no puedes asistir, avísanos con al menos 24 h de anticipación.</li>
<li>Somos pet friendly: tu mascota es bienvenida.</li>
<li>Contamos con respaldo eléctrico: un apagón no afecta tu cita.</li></ul></div></td></tr>
<tr><td align="center" class="pad" style="padding:8px 40px 34px;">
<a href="{escape(config.MAPS_URL, quote=True)}" style="color:{BROWN};font-size:13px;font-weight:600;font-family:{FONT};">Cómo llegar</a>
&nbsp;·&nbsp;<a href="{escape(config.INSTAGRAM_URL, quote=True)}" style="color:{BROWN};font-size:13px;font-weight:600;font-family:{FONT};">@mocca.val</a></td></tr>"""
    return subject, _shell("Cita confirmada", body)


# ── Envío ────────────────────────────────────────────────────────────────────
def _send(payload: dict) -> None:
    r = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
        json=payload,
        timeout=20,
    )
    if r.status_code >= 400:
        log.error("Resend %s: %s", r.status_code, r.text)
        r.raise_for_status()


def send_studio_email(v: CitaView) -> None:
    if not (config.RESEND_API_KEY and config.STUDIO_EMAILS):
        log.info("Resend/STUDIO_EMAILS sin configurar: omito email al estudio")
        return
    subject, html = studio_email(v)
    payload = {"from": config.MAIL_FROM, "to": config.STUDIO_EMAILS[:1], "subject": subject, "html": html}
    if len(config.STUDIO_EMAILS) > 1:
        payload["cc"] = config.STUDIO_EMAILS[1:]
    _send(payload)


def send_client_email(v: CitaView) -> None:
    if not (config.RESEND_API_KEY and v.email):
        return
    subject, html = client_email(v)
    ics = base64.b64encode(build_ics(v).encode()).decode()
    payload = {
        "from": config.MAIL_FROM,
        "to": [v.email],
        "subject": subject,
        "html": html,
        "attachments": [{"filename": "cita-mocca.ics", "content": ics, "content_type": "text/calendar"}],
    }
    if config.REPLY_TO:
        payload["reply_to"] = config.REPLY_TO
    _send(payload)
