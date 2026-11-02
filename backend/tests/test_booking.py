from datetime import datetime

from app import emailer, google_client, logic
from app.emailer import CitaView, ItemView

from .conftest import TUESDAY, payload

H = "/webhook/mocca_beauty"
C = "/webhook/citamocca"
ALL = ["9:00 am", "10:30 am", "12:30 pm", "2:00 pm", "3:30 pm"]


def slots(client, **kw):
    return client.post(H, json=payload(**kw)).json()["disponibles"]


def book(client, horario, **kw):
    return client.post(C, json=payload(horario=horario, **kw))


def test_empty_day_has_all_slots(client):
    assert slots(client) == ALL


def test_closed_days_and_past_dates(client):
    assert slots(client, fecha="2026-11-08") == []  # domingo
    assert slots(client, fecha="2026-11-09") == []  # lunes
    assert slots(client, fecha="2026-10-30") == []  # pasado


def test_double_booking_same_staff_is_409(client):
    assert book(client, "9:00 am", manicurista="Anabel").status_code == 200
    r = book(client, "9:00 am", manicurista="Anabel")
    assert r.status_code == 409
    assert "9:00 am" not in slots(client, manicurista="Anabel")
    assert "9:00 am" in slots(client, manicurista="Edu")


def test_sin_preferencia_edu_first_then_anabel_then_full(client):
    assert book(client, "9:00 am").json()["manicuristas"] == ["Edu"]
    assert book(client, "9:00 am").json()["manicuristas"] == ["Anabel"]
    assert book(client, "9:00 am").status_code == 409
    assert "9:00 am" not in slots(client)


def test_jelly_blocks_next_slot(client):
    # Jelly = 120 min: 9:00 → 11:00, pisa el bloque de 10:30
    assert book(client, "9:00 am", manicurista="Edu", servicios=["Manicure + Jelly Tips"]).status_code == 200
    edu = slots(client, manicurista="Edu")
    assert "9:00 am" not in edu and "10:30 am" not in edu and "12:30 pm" in edu
    assert "10:30 am" in slots(client, manicurista="Anabel")


def test_two_services_add_duration(client):
    assert logic.duration(["Manicure Tradicional", "Pedicure Tradicional"]) == 180
    book(client, "9:00 am", manicurista="Edu", servicios=["Manicure Tradicional", "Pedicure Tradicional"])
    edu = slots(client, manicurista="Edu")
    assert "10:30 am" not in edu and "12:30 pm" in edu


def test_express_needs_both_and_books_both(client):
    ex = dict(isExpress=True, servicios=["[SERVICIO EXPRESS]", "Manicure Tradicional", "Pedicure Semipermanente"])
    r = book(client, "10:30 am", **ex)
    assert r.status_code == 200 and sorted(r.json()["manicuristas"]) == ["Anabel", "Edu"]
    assert "10:30 am" not in slots(client)  # nadie libre ahí
    assert "10:30 am" not in slots(client, **ex)
    # si Edu queda ocupada, express no está disponible aunque Anabel esté libre
    book(client, "9:00 am", manicurista="Edu")
    assert "9:00 am" not in slots(client, **ex)
    assert "9:00 am" in slots(client, manicurista="Anabel")


def test_ninia_alias_maps_to_anabel(client):
    assert book(client, "2:00 pm", manicurista="Ninia").json()["manicuristas"] == ["Anabel"]


def test_google_manual_block_hides_slot(client, monkeypatch):
    block = (datetime(2026, 11, 3, 12, 0), datetime(2026, 11, 3, 13, 0))
    monkeypatch.setattr(google_client, "busy_by_staff", lambda a, b: {"Edu": [block], "Anabel": [block]})
    s = slots(client)
    assert "12:30 pm" not in s  # pisa el bloqueo manual 12:00-13:00
    assert "10:30 am" in s and "9:00 am" in s and "2:00 pm" in s  # 10:30-12:00 sigue libre


def test_today_hides_past_slots(client, monkeypatch):
    monkeypatch.setattr(logic, "now_local", lambda: datetime(2026, 11, 3, 11, 0))
    assert slots(client) == ["12:30 pm", "2:00 pm", "3:30 pm"]


def test_requires_service_and_valid_slot(client):
    assert book(client, "9:00 am", servicios=[]).status_code == 400
    assert book(client, "8:00 am").status_code == 400


def test_post_booking_runs_without_credentials(client):
    from app.notifications import run_post_booking

    cid = book(client, "9:00 am", email="ana@example.com").json()["id"]
    run_post_booking(cid)  # sin Google/Resend configurados no debe lanzar excepciones


# ── Emails ───────────────────────────────────────────────────────────────────
def _view(nombre="Ana Pérez"):
    from datetime import date

    return CitaView(
        id=7, nombre=nombre, telefono="04121234567", email="ana@example.com", fecha=date(2026, 11, 3), horario="9:00 am", is_express=True,
        items=[
            ItemView("Edu", "Manicure Tradicional", 90, datetime(2026, 11, 3, 9, 0), datetime(2026, 11, 3, 10, 30)),
            ItemView("Anabel", "Pedicure Semipermanente", 90, datetime(2026, 11, 3, 9, 0), datetime(2026, 11, 3, 10, 30), auto=True),
        ],
    )


def test_email_escapes_html_and_builds_links():
    _, html = emailer.studio_email(_view("<script>alert(1)</script>"))
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "wa.me/584121234567" in html
    _, chtml = emailer.client_email(_view())
    assert "calendar.google.com/calendar/render" in chtml
    assert "dates=20261103T130000Z%2F20261103T143000Z" in emailer.google_calendar_link(_view())


def test_ics_is_utc_and_valid():
    ics = emailer.build_ics(_view())
    assert "DTSTART:20261103T130000Z" in ics and "DTEND:20261103T143000Z" in ics
    assert ics.startswith("BEGIN:VCALENDAR") and ics.rstrip().endswith("END:VCALENDAR")


def test_wa_number_normalizes():
    assert emailer.wa_number("0412-123 4567") == "584121234567"
    assert emailer.wa_number("+58 412 1234567") == "584121234567"
    assert emailer.wa_number("4121234567") == "584121234567"
