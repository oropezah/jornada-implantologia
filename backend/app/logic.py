"""Reglas de negocio de Mocca (portadas de n8n y corregidas).

- 5 horarios fijos; cada servicio dura 90 min, Jelly 120 min; varios servicios suman duración.
- La disponibilidad cruza la base de datos con Google Calendar (bloqueos manuales incluidos).
- Servicio Express: Edu hace manos y Anabel pies, EN PARALELO (ambas deben estar libres).
- "Sin preferencia": Edu primero; si está ocupada, Anabel.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import google_client
from .config import CLOSED_WEEKDAYS, DURATION_JELLY, DURATION_STANDARD, SLOTS, STAFF_ALIASES, STAFF_PRIORITY, TIMEZONE
from .models import Cita, CitaStaff
from .schemas import BookingRequest

TZ = ZoneInfo(TIMEZONE)
NO_PREF = "sin preferencia"
MANOS_RE = re.compile(r"manicure|manos", re.I)
PIES_RE = re.compile(r"pedicure|pies", re.I)
JELLY_RE = re.compile(r"jelly", re.I)


class BookingError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


@dataclass
class Need:
    staff: str | None  # None = cualquiera
    servicios: list[str]
    minutes: int


@dataclass
class Assignment:
    staff: str
    servicio: str
    minutes: int
    start: datetime
    end: datetime
    auto: bool


# ── Tiempo ───────────────────────────────────────────────────────────────────
def now_local() -> datetime:
    return datetime.now(TZ).replace(tzinfo=None)


def parse_fecha(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise BookingError(400, "Fecha inválida (usa YYYY-MM-DD).")


def max_booking_date(today: date) -> date:
    # Igual que el calendario del frontend: 30 días, y diciembre siempre disponible.
    return max(today + timedelta(days=30), date(today.year, 12, 31))


def date_bookable(fecha: date) -> bool:
    today = now_local().date()
    return today <= fecha <= max_booking_date(today) and fecha.weekday() not in CLOSED_WEEKDAYS


def slot_start(fecha: date, label: str) -> datetime:
    return datetime.combine(fecha, datetime.strptime(label, "%I:%M %p").time())


# ── Servicios y necesidades ──────────────────────────────────────────────────
def clean_services(servicios: list[str]) -> list[str]:
    # Quita etiquetas decorativas como "[SERVICIO EXPRESS]"
    return [s.strip() for s in servicios if isinstance(s, str) and s.strip() and not s.strip().startswith("[")]


def duration(servicios: list[str]) -> int:
    if not servicios:
        return DURATION_STANDARD
    return sum(DURATION_JELLY if JELLY_RE.search(s) else DURATION_STANDARD for s in servicios)


def is_express(req: BookingRequest) -> bool:
    return req.isExpress or "EXPRESS" in (req.encabezado or "").upper() or any("express" in s.lower() for s in req.servicios)


def resolve_staff(name: str | None) -> str | None:
    n = (name or "").strip().lower()
    if not n or n == NO_PREF:
        return None
    for staff in STAFF_PRIORITY:
        if staff.lower() == n:
            return staff
    if n in STAFF_ALIASES:
        return STAFF_ALIASES[n]
    raise BookingError(400, "Manicurista inválida.")


def build_needs(req: BookingRequest) -> list[Need]:
    servs = clean_services(req.servicios)
    if is_express(req):
        manos = next((s for s in servs if MANOS_RE.search(s)), None) or (servs[0] if servs else "Manos Express")
        pies = next((s for s in servs if PIES_RE.search(s)), None) or (servs[1] if len(servs) > 1 else "Pies Express")
        return [Need("Edu", [manos], duration([manos])), Need("Anabel", [pies], duration([pies]))]
    return [Need(resolve_staff(req.manicurista), servs, duration(servs))]


# ── Disponibilidad ───────────────────────────────────────────────────────────
def _overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def busy_for_day(session: Session, fecha: date) -> dict[str, list[tuple[datetime, datetime]]]:
    day_start = datetime.combine(fecha, time.min)
    day_end = day_start + timedelta(days=1)
    rows = session.execute(
        select(CitaStaff.staff, CitaStaff.starts_at, CitaStaff.ends_at)
        .join(Cita, Cita.id == CitaStaff.cita_id)
        .where(Cita.status == "confirmada", CitaStaff.starts_at < day_end, CitaStaff.ends_at > day_start)
    ).all()
    busy: dict[str, list[tuple[datetime, datetime]]] = {s: [] for s in STAFF_PRIORITY}
    for staff, a, b in rows:
        busy.setdefault(staff, []).append((a, b))
    for staff, spans in google_client.busy_by_staff(day_start, day_end).items():
        busy.setdefault(staff, []).extend(spans)
    return busy


def find_assignment(needs: list[Need], busy: dict, start: datetime) -> list[Assignment] | None:
    used: set[str] = set()
    out: list[Assignment] = []
    for need in needs:
        end = start + timedelta(minutes=need.minutes)
        candidates = [need.staff] if need.staff else [s for s in STAFF_PRIORITY if s not in used]
        chosen = next(
            (s for s in candidates if s not in used and not any(_overlap(start, end, b0, b1) for b0, b1 in busy.get(s, []))),
            None,
        )
        if chosen is None:
            return None
        used.add(chosen)
        out.append(Assignment(chosen, " + ".join(need.servicios), need.minutes, start, end, auto=need.staff is None))
    return out


def available_slots(session: Session, req: BookingRequest) -> list[str]:
    fecha = parse_fecha(req.fecha)
    if not date_bookable(fecha):
        return []
    needs = build_needs(req)
    busy = busy_for_day(session, fecha)
    now = now_local()
    return [
        label
        for label in SLOTS
        if slot_start(fecha, label) > now and find_assignment(needs, busy, slot_start(fecha, label)) is not None
    ]


# ── Reserva ──────────────────────────────────────────────────────────────────
def create_cita(session: Session, req: BookingRequest) -> Cita:
    if not req.horario or req.horario not in SLOTS:
        raise BookingError(400, "Horario inválido.")
    fecha = parse_fecha(req.fecha)
    if not date_bookable(fecha):
        raise BookingError(400, "Ese día no está disponible.")
    start = slot_start(fecha, req.horario)
    if start <= now_local():
        raise BookingError(400, "Ese horario ya pasó.")
    express = is_express(req)
    if not express and not clean_services(req.servicios):
        raise BookingError(400, "Selecciona al menos un servicio.")

    needs = build_needs(req)
    assignments = find_assignment(needs, busy_for_day(session, fecha), start)
    if assignments is None:
        raise BookingError(409, "Ese horario ya fue tomado. Elige otro.")

    cita = Cita(
        nombre=req.nombre.strip(),
        fecha_nacimiento=req.fechaNacimiento or "",
        telefono=req.telefono.strip(),
        email=req.email,
        servicios=clean_services(req.servicios),
        is_express=express,
        manicurista_pedida=req.manicurista or "Sin preferencia",
        fecha=fecha,
        horario=req.horario,
        staff=[
            CitaStaff(
                staff=a.staff,
                servicio=a.servicio or "Servicio no especificado",
                minutos=a.minutes,
                auto_asignada=a.auto,
                starts_at=a.start,
                ends_at=a.end,
            )
            for a in assignments
        ],
    )
    session.add(cita)
    try:
        session.commit()  # la restricción EXCLUDE de Postgres resuelve carreras entre dos clientes
    except IntegrityError:
        session.rollback()
        raise BookingError(409, "Ese horario ya fue tomado. Elige otro.")
    return cita
