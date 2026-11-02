"""Genera previews HTML de los emails para verlos en el navegador:  python scripts/preview_emails.py"""
import os
import pathlib
import sys
from datetime import date, datetime

os.environ.setdefault("DATABASE_URL", "sqlite:///preview.db")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import emailer  # noqa: E402
from app.emailer import CitaView, ItemView  # noqa: E402

view = CitaView(
    id=1, nombre="María González", telefono="04121234567", email="maria@example.com",
    fecha=date(2026, 12, 4), horario="10:30 am", is_express=True, fecha_nacimiento="1994-05-12",
    items=[
        ItemView("Edu", "Manicure + Rubber Gel", 90, datetime(2026, 12, 4, 10, 30), datetime(2026, 12, 4, 12, 0)),
        ItemView("Anabel", "Pedicure Semipermanente", 90, datetime(2026, 12, 4, 10, 30), datetime(2026, 12, 4, 12, 0)),
    ],
)
out = pathlib.Path(__file__).resolve().parent.parent / "previews"
out.mkdir(exist_ok=True)
(out / "email-estudio.html").write_text(emailer.studio_email(view)[1], encoding="utf-8")
(out / "email-cliente.html").write_text(emailer.client_email(view)[1], encoding="utf-8")
print("Listo → previews/email-estudio.html y previews/email-cliente.html")
