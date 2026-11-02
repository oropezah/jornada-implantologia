import os

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _db_url() -> str:
    url = _env("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta la variable DATABASE_URL (connection string de Neon).")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _db_url()
ALLOWED_ORIGINS = [o.strip() for o in _env("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
TIMEZONE = _env("TIMEZONE", "America/Caracas")

# ── Negocio ──────────────────────────────────────────────────────────────────
SLOTS = ["9:00 am", "10:30 am", "12:30 pm", "2:00 pm", "3:30 pm"]
CLOSED_WEEKDAYS = {0, 6}  # lunes=0 ... domingo=6
DURATION_STANDARD = 90  # min por servicio normal
DURATION_JELLY = 120  # min por servicio Jelly

# Orden de prioridad para "Sin preferencia" (igual que n8n: Edu primero, si está ocupada Anabel)
STAFF_PRIORITY = ["Edu", "Anabel"]
# En n8n la manicurista se llamaba "Ninia". Si llega ese nombre, es Anabel.
STAFF_ALIASES = {"ninia": "Anabel"}

# ── Google (service account) ─────────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON = _env("GOOGLE_SERVICE_ACCOUNT_JSON")  # el JSON completo en una variable
GOOGLE_SERVICE_ACCOUNT_FILE = _env("GOOGLE_SERVICE_ACCOUNT_FILE")  # alternativa local (no subir a git)
CALENDARS = {
    "Anabel": _env("CALENDAR_ID_ANABEL"),  # el calendario que en n8n se llamaba "Ninia"
    "Edu": _env("CALENDAR_ID_EDU"),
}
SHEET_ID = _env("SHEET_ID")
SHEET_RANGE = _env("SHEET_RANGE", "Sheet1!A:J")

# ── Resend ───────────────────────────────────────────────────────────────────
RESEND_API_KEY = _env("RESEND_API_KEY")
MAIL_FROM = _env("MAIL_FROM", "Mocca Beauty Studio <onboarding@resend.dev>")
STUDIO_EMAILS = [e.strip() for e in _env("STUDIO_EMAILS").split(",") if e.strip()]
REPLY_TO = _env("REPLY_TO") or (STUDIO_EMAILS[0] if STUDIO_EMAILS else "")

# ── WhatsApp (YCloud) · opcional ─────────────────────────────────────────────
YCLOUD_API_KEY = _env("YCLOUD_API_KEY")
YCLOUD_FROM = _env("YCLOUD_FROM")  # número emisor, ej 584221638753
YCLOUD_TO = _env("YCLOUD_TO")  # número del estudio que recibe el aviso
YCLOUD_TEMPLATE = _env("YCLOUD_TEMPLATE", "cita_mocca")

STUDIO_NAME = "Mocca Beauty Studio"
STUDIO_LOCATION = "Mocca Beauty Studio, Valencia, Venezuela"
MAPS_URL = "https://www.google.com/maps/place/Mocca+Beauty+Studio/@10.1993157,-68.0140155,17z"
INSTAGRAM_URL = "https://www.instagram.com/mocca.val/"
