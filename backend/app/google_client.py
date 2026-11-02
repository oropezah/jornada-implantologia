"""Google Calendar + Sheets con service account (mismo enfoque que Jornada Implantología).

- Calendar: los calendarios de Edu y Anabel deben estar compartidos con el email de la service account
  con permiso "Hacer cambios en eventos".
- Sheets: la hoja debe estar compartida con la service account como Editor.
Si no hay credenciales, todo degrada con gracia (la disponibilidad usa solo la base de datos).
"""

import json
import logging
from datetime import datetime, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from . import config

log = logging.getLogger("mocca.google")
TZ = ZoneInfo(config.TIMEZONE)
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/spreadsheets"]


def _credentials():
    from google.oauth2 import service_account

    if config.GOOGLE_SERVICE_ACCOUNT_JSON:
        info = json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if config.GOOGLE_SERVICE_ACCOUNT_FILE:
        return service_account.Credentials.from_service_account_file(config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return None


@lru_cache(maxsize=1)
def _service(name: str, version: str):
    from googleapiclient.discovery import build

    creds = _credentials()
    if creds is None:
        return None
    return build(name, version, credentials=creds, cache_discovery=False)


def calendar_enabled() -> bool:
    return _credentials_available() and any(config.CALENDARS.values())


def sheets_enabled() -> bool:
    return _credentials_available() and bool(config.SHEET_ID)


def _credentials_available() -> bool:
    return bool(config.GOOGLE_SERVICE_ACCOUNT_JSON or config.GOOGLE_SERVICE_ACCOUNT_FILE)


def _to_local_naive(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ).replace(tzinfo=None)


def busy_by_staff(day_start: datetime, day_end: datetime) -> dict[str, list[tuple[datetime, datetime]]]:
    """Intervalos ocupados por manicurista en Google Calendar (incluye bloqueos manuales de la asistente).
    Si Google falla devuelve {} y se loguea: la reserva sigue protegida por la base de datos."""
    if not calendar_enabled():
        return {}
    try:
        svc = _service("calendar", "v3")
        items = [{"id": cid} for cid in config.CALENDARS.values() if cid]
        body = {
            "timeMin": day_start.replace(tzinfo=TZ).isoformat(),
            "timeMax": day_end.replace(tzinfo=TZ).isoformat(),
            "timeZone": config.TIMEZONE,
            "items": items,
        }
        res = svc.freebusy().query(body=body).execute()
        out: dict[str, list[tuple[datetime, datetime]]] = {}
        for staff, cid in config.CALENDARS.items():
            cal = res.get("calendars", {}).get(cid)
            if not cal:
                continue
            if cal.get("errors"):
                log.warning("Calendar %s (%s) no accesible: %s. ¿Lo compartiste con la service account?", staff, cid, cal["errors"])
                continue
            out[staff] = [(_to_local_naive(b["start"]), _to_local_naive(b["end"])) for b in cal.get("busy", [])]
        return out
    except Exception:  # noqa: BLE001
        log.exception("Fallo consultando Google Calendar; uso solo la base de datos")
        return {}


def create_event(staff: str, summary: str, description: str, start: datetime, end: datetime) -> str | None:
    cid = config.CALENDARS.get(staff)
    if not (calendar_enabled() and cid):
        return None
    svc = _service("calendar", "v3")
    body = {
        "summary": summary,
        "description": description,
        "location": config.STUDIO_LOCATION,
        "start": {"dateTime": start.replace(tzinfo=TZ).isoformat(), "timeZone": config.TIMEZONE},
        "end": {"dateTime": end.replace(tzinfo=TZ).isoformat(), "timeZone": config.TIMEZONE},
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 60}]},
    }
    return svc.events().insert(calendarId=cid, body=body).execute()["id"]


def append_rows(rows: list[list[str]]) -> None:
    if not sheets_enabled():
        return
    svc = _service("sheets", "v4")
    svc.spreadsheets().values().append(
        spreadsheetId=config.SHEET_ID,
        range=config.SHEET_RANGE,
        valueInputOption="RAW",  # RAW conserva el 0 inicial de los teléfonos
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
