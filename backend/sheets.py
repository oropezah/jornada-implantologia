import json
import os
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
    if ws.cell(1, 1).value != HEADERS[0]:
        ws.insert_row(HEADERS, 1)
    elif ws.cell(1, len(HEADERS)).value != HEADERS[-1]:
        # Hoja creada antes de agregar la columna del comprobante
        ws.update_cell(1, len(HEADERS), HEADERS[-1])


def cedula_exists(cedula: str) -> bool:
    ws = _worksheet()
    cedulas = {c.strip() for c in ws.col_values(3)[1:]}
    return cedula in cedulas


def append_attendee(d: dict) -> None:
    ws = _worksheet()
    _ensure_headers(ws)

    cedulas = {c.strip() for c in ws.col_values(3)[1:]}
    if d["cedula"] in cedulas:
        raise DuplicateAttendee()

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        d["nombre"],
        d["cedula"],
        d["correo"],
        d["telefono"],
        d["institucion"],
        "Por verificar",
        d.get("comprobante_url", ""),
    ]
    ws.append_row(row, value_input_option="RAW")