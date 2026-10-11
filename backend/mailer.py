import logging
import os
import smtplib
from email.message import EmailMessage
from html import escape

log = logging.getLogger("jornada.mail")

EVENT = "III Jornada de Actualización en Implantología Bucal"
IG_URL = "https://instagram.com/synco.ia"


def _first(name: str) -> str:
    parts = name.split()
    return parts[0] if parts else name


def _row(label: str, value: str) -> str:
    return (
        "<tr>"
        '<td style="padding:8px 0;color:#5b6e80">' + label + "</td>"
        '<td style="padding:8px 0;text-align:right;font-weight:600;color:#2c4255">'
        + escape(value)
        + "</td>"
        "</tr>"
    )


def _html(d: dict) -> str:
    first = escape(_first(d["nombre"]))
    phone = escape(d["telefono"])
    rows = (
        _row("Nombre", d["nombre"])
        + _row("Cédula", d["cedula"])
        + _row("Teléfono", d["telefono"])
        + _row("Institución", d["institucion"])
    )
    return f"""\
<div style="background:#f0f4f8;padding:24px;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:20px;overflow:hidden">
    <div style="background:#2c4255;color:#fff;padding:28px">
      <div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#b8d1e1">Universidad de Carabobo</div>
      <div style="font-size:22px;font-weight:700;margin-top:8px">{EVENT}</div>
    </div>
    <div style="padding:28px;color:#1e293b">
      <p style="font-size:18px;font-weight:700;color:#2c4255;margin:0 0 8px">¡Inscripción agendada, {first}!</p>
      <p style="color:#5b6e80;margin:0 0 18px">Tu lugar quedó registrado. 21 de noviembre de 2026 · Instituto Docente de Urología.</p>
      <table style="width:100%;border-collapse:collapse;border-top:1px solid #dbe6ee;border-bottom:1px solid #dbe6ee">{rows}</table>
      <p style="margin:18px 0 0"><b>Estado de tu inscripción:</b> Hemos recibido tu comprobante de pago. Verificaremos los datos y te confirmaremos en breve.</p>
      <p style="margin:24px 0 0;padding-top:16px;border-top:1px solid #dbe6ee;font-size:12px;color:#5b6e80;text-align:center">
        Este reporte fue hecho por <a href="{IG_URL}" style="color:#0088cc;font-weight:600;text-decoration:none">Synco</a>
      </p>
    </div>
  </div>
</div>"""


def send_confirmation_email(d: dict) -> None:
    try:
        user = os.environ["GMAIL_USER"]
        password = os.environ["GMAIL_APP_PASSWORD"]
        sender_name = os.getenv("MAIL_FROM_NAME", EVENT)
        first = _first(d["nombre"])

        text = (
            "Hola " + first + ", tu inscripción a la " + EVENT
            + " quedó agendada para el 21 de noviembre de 2026.\n"
            + "Hemos recibido tu comprobante de pago. Verificaremos los datos y te confirmaremos en breve.\n\n"
            + "Este reporte fue hecho por Synco (" + IG_URL + ")"
        )

        msg = EmailMessage()
        msg["Subject"] = "Confirmación de inscripción · " + EVENT
        msg["From"] = sender_name + " <" + user + ">"
        msg["To"] = d["correo"]
        msg.set_content(text)
        msg.add_alternative(_html(d), subtype="html")

        # Conexión por puerto 587 usando STARTTLS
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user, password)
            s.send_message(msg)

        log.info("Correo enviado exitosamente a %s", d.get("correo"))

    except Exception:
        log.exception("No se pudo enviar el correo a %s", d.get("correo"))