"""Tareas que corren DESPUÉS de confirmar la cita (la respuesta al cliente no espera a Google/Resend).
Cada paso es independiente: si uno falla se loguea y los demás siguen."""

import logging

from sqlalchemy.orm import selectinload

from . import emailer, google_client, whatsapp
from .db import SessionLocal
from .models import Cita

log = logging.getLogger("mocca.notify")

SERVICIO_LABEL = {"Edu": "Manos", "Anabel": "Pies"}


def _safe(name: str, fn, *args) -> None:
    try:
        fn(*args)
    except Exception:  # noqa: BLE001
        log.exception("Falló el paso '%s'", name)


def to_view(cita: Cita) -> emailer.CitaView:
    return emailer.CitaView(
        id=cita.id,
        nombre=cita.nombre,
        telefono=cita.telefono,
        email=cita.email,
        fecha=cita.fecha,
        horario=cita.horario,
        is_express=cita.is_express,
        fecha_nacimiento=cita.fecha_nacimiento,
        items=[
            emailer.ItemView(r.staff, r.servicio, r.minutos, r.starts_at, r.ends_at, r.auto_asignada) for r in cita.staff
        ],
    )


def _event_texts(cita: Cita, row) -> tuple[str, str]:
    if cita.is_express:
        summary = f"[Express {SERVICIO_LABEL.get(row.staff, '')}] {row.servicio} - {cita.nombre}"
    else:
        summary = f"{row.servicio} - {cita.nombre}"
    auto = " (asignada automáticamente)" if row.auto_asignada else ""
    lines = [
        f"👤 Cliente: {cita.nombre}",
        f"📞 Teléfono: {cita.telefono}",
        f"🎂 F. Nacimiento: {cita.fecha_nacimiento or 'N/A'}",
        f"💅 Servicio: {row.servicio}",
        f"👩‍🎨 Manicurista: {row.staff}{auto}",
        f"⏱️ Duración: {row.minutos} min",
    ]
    if cita.email:
        lines.append(f"✉️ Email: {cita.email}")
    if cita.is_express:
        lines.append("⚡ Servicio Express en paralelo")
    return summary, "\n".join(lines)


def _create_events(session, cita: Cita) -> None:
    for row in cita.staff:
        summary, desc = _event_texts(cita, row)
        row.google_event_id = google_client.create_event(row.staff, summary, desc, row.starts_at, row.ends_at)
    session.commit()


def _append_sheet(cita: Cita) -> None:
    rows = [
        [
            cita.nombre,
            cita.telefono,
            r.servicio,
            r.staff,
            cita.fecha.isoformat(),
            cita.horario,
            "",  # Cedula (ya no se pide)
            cita.fecha_nacimiento or "",
            "false",  # Promo
            cita.email or "",
        ]
        for r in cita.staff
    ]
    google_client.append_rows(rows)


def run_post_booking(cita_id: int) -> None:
    with SessionLocal() as session:
        cita = session.get(Cita, cita_id, options=[selectinload(Cita.staff)])
        if cita is None:
            return
        view = to_view(cita)
        _safe("google_calendar", _create_events, session, cita)
        _safe("google_sheets", _append_sheet, cita)
        _safe("email_estudio", emailer.send_studio_email, view)
        _safe("email_cliente", emailer.send_client_email, view)
        _safe("whatsapp_estudio", whatsapp.notify_studio, view)
