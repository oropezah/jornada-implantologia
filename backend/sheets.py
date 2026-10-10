import json
import os
import re
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


def _clean_cedula(val: str) -> str:
    """Extrae únicamente los dígitos numéricos de la cédula."""
    if not val:
        return ""
    return re.sub(r"\D", "", str(val))


def _client() -> gspread.Client:
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        return gspread.service_account_from_dict(json.loads(raw))
    filename = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    return gspread.service_account(filename=filename)


def _worksheet():
    sheet = _client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
    return sheet.sheet1


def _ensure_headers(ws) -> None:
    try:
        if ws.cell(1, 1).value != HEADERS[0]:
            ws.insert_row(HEADERS, 1)
        elif ws.cell(1, len(HEADERS)).value != HEADERS[-1]:
            ws.update_cell(1, len(HEADERS), HEADERS[-1])
    except Exception:
        pass


def cedula_exists(cedula: str) -> bool:
    target = _clean_cedula(cedula)
    if not target:
        return False

    try:
        ws = _worksheet()
        col3_values = ws.col_values(3)[1:]  # Salta los encabezados
        existing_cedulas = {_clean_cedula(c) for c in col3_values if c}
        return target in existing_cedulas
    except Exception as e:
        print(f"Error al verificar cédula en Sheets: {e}")
        return False


def append_attendee(d: dict) -> None:
    ws = _worksheet()
    _ensure_headers(ws)

    target_cedula = _clean_cedula(d.get("cedula", ""))

    # Verificar cédulas existentes comparando únicamente dígitos
    col3_values = ws.col_values(3)[1:]
    existing_cedulas = {_clean_cedula(c) for c in col3_values if c}

    if target_cedula and target_cedula in existing_cedulas:
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
    ws.append_row(row, value_input_option="RAW")