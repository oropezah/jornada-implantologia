import logging
import os
from html import escape
import resend

log = logging.getLogger("jornada.mail")

EVENT = "III Jornada de Actualización en Implantología Bucal"
IG_URL = "https://instagram.com/synco.ia"


def _first(name: str) -> str:
    parts = name.split()
    return parts[0] if parts else name


def _row(label: str, value: str) -> str:
    return f"""\
<tr>
  <td style="padding:12px 0;color:#64748b;font-size:13px;border-bottom:1px solid #f1f5f9">{label}</td>
  <td style="padding:12px 0;text-align:right;font-weight:600;color:#0f172a;font-size:13px;border-bottom:1px solid #f1f5f9">{escape(value)}</td>
</tr>"""


def _html(d: dict) -> str:
    first = escape(_first(d["nombre"]))
    rows = (
        _row("Nombre", d["nombre"])
        + _row("Cédula", d["cedula"])
        + _row("Teléfono", d["telefono"])
        + _row("Institución", d["institucion"])
    )
    return f"""\
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Inter',Segoe UI,sans-serif">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#0f172a;padding:40px 12px">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:540px;background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 20px 25px -5px rgba(0,0,0,0.3)">
          
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%);padding:36px 32px;border-bottom:1px solid #334155">
              <span style="display:inline-block;padding:6px 14px;background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.3);border-radius:999px;color:#38bdf8;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase">
                &bull; Inscripción Registrada
              </span>
              <h1 style="color:#ffffff;font-size:22px;font-weight:700;margin:18px 0 6px;line-height:1.3;letter-spacing:-0.02em">
                {EVENT}
              </h1>
              <p style="color:#94a3b8;font-size:12px;margin:0;letter-spacing:0.08em;text-transform:uppercase;font-weight:500">
                Universidad de Carabobo
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px">
              <h2 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 10px;letter-spacing:-0.01em">
                &#128075; ¡Todo listo, {first}!
              </h2>
              <p style="color:#475569;font-size:14px;line-height:1.6;margin:0 0 24px">
                Tu registro ha sido procesado de manera exitosa. A continuación te presentamos el resumen de tu solicitud:
              </p>

              <!-- Box Date -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;margin-bottom:28px">
                <tr>
                  <td style="padding:16px 20px">
                    <div style="font-size:11px;font-weight:700;color:#0284c7;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">
                      &#128197; Fecha &amp; Ubicación
                    </div>
                    <div style="font-size:14px;font-weight:700;color:#0f172a">
                      21 de Noviembre de 2026
                    </div>
                    <div style="font-size:12px;color:#64748b;margin-top:2px">
                      Instituto Docente de Urología
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Ticket Table -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-collapse:collapse;margin-bottom:28px">
                {rows}
              </table>

              <!-- Status Box -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background:#f0f9ff;border-left:3px solid #38bdf8;border-radius:0 12px 12px 0;margin-bottom:28px">
                <tr>
                  <td style="padding:16px">
                    <p style="margin:0;font-size:13px;color:#0369a1;line-height:1.5">
                      <b>Estatus:</b> Comprobante en revisión. Verificaremos los datos ingresados y te confirmaremos en breve.
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Footer -->
              <div style="border-top:1px solid #f1f5f9;padding-top:24px;text-align:center">
                <p style="margin:0;font-size:12px;color:#94a3b8">
                  Desarrollado con precisión por 
                  <a href="{IG_URL}" style="color:#0284c7;font-weight:600;text-decoration:none">Synco</a>
                </p>
              </div>

            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_confirmation_email(d: dict) -> None:
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        first = _first(d["nombre"])

        text = (
            "Hola " + first + ", tu inscripción a la " + EVENT
            + " quedó agendada para el 21 de noviembre de 2026.\n"
            + "Hemos recibido tu comprobante de pago. Verificaremos los datos y te confirmaremos en breve.\n\n"
            + "Este reporte fue hecho por Synco (" + IG_URL + ")"
        )

        params = {
            "from": f"{EVENT} <onboarding@resend.dev>",
            "to": [d["correo"]],
            "subject": f"Confirmación de inscripción · {EVENT}",
            "text": text,
            "html": _html(d),
        }

        resend.Emails.send(params)
        log.info("Correo enviado exitosamente vía Resend API a %s", d.get("correo"))

    except Exception:
        log.exception("No se pudo enviar el correo a %s", d.get("correo"))