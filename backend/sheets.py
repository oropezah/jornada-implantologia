import json
import os
import re
import threading
from datetime import datetime

import gspread

HEADERS = [
    "Fecha",
    "Nombre completo",
    "Cédula",
    "Correo",
    "Teléfono",
    "Institución",
    "Estado de pago",
    "Comprobante (Drive)",
]


class DuplicateAttendee(Exception):
    pass


_lock = threading.Lock()
_ws = None


def _clean_cedula(val) -> str:
    """Extrae únicamente los dígitos de la cédula."""
    if not val:
        return ""
    return re.sub(r"\D", "", str(val))


def _client() -> gspread.Client:
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        return gspread.service_account_from_dict(json.loads(raw))
    filename = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    return gspread.service_account(filename=filename)


def _ensure_headers(ws) -> None:
    try:
        if ws.cell(1, 1).value != HEADERS[0]:
            ws.insert_row(HEADERS, 1)
        elif ws.cell(1, len(HEADERS)).value != HEADERS[-1]:
            ws.update_cell(1, len(HEADERS), HEADERS[-1])
    except Exception:
        pass


def _worksheet():
    """Hoja en caché: se autentica una sola vez, no en cada petición."""
    global _ws
    with _lock:
        if _ws is None:
            ws = _client().open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1
            _ensure_headers(ws)
            _ws = ws
        return _ws


def _reset() -> None:
    global _ws
    with _lock:
        _ws = None


def _existing(ws) -> set:
    return {_clean_cedula(c) for c in ws.col_values(3)[1:] if c}


def cedula_exists(cedula: str) -> bool:
    target = _clean_cedula(cedula)
    if not target:
        return False
    try:
        return target in _existing(_worksheet())
    except Exception:
        _reset()  # reconecta y reintenta una vez
        return target in _existing(_worksheet())


def append_attendee(d: dict, check_duplicate: bool = True) -> None:
    ws = _worksheet()

    if check_duplicate:
        target = _clean_cedula(d.get("cedula", ""))
        if target and target in _existing(ws):
            raise DuplicateAttendee()

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        d.get("nombre", "").strip(),
        str(d.get("cedula", "")).strip(),
        d.get("correo", "").strip(),
        d.get("telefono", "").strip(),
        d.get("institucion", "").strip(),
        "Por verificar",
        d.get("comprobante_url", ""),
    ]
    try:
        ws.append_row(row, value_input_option="RAW")
    except Exception:
        _reset()
        raise