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
  <td style="padding:12px 16px;color:#5b738a;font-size:13px;border-bottom:1px solid #e2e8f0;font-weight:500">{label}</td>
  <td style="padding:12px 16px;text-align:right;font-weight:700;color:#1c2a39;font-size:13px;border-bottom:1px solid #e2e8f0">{escape(value)}</td>
</tr>"""


def _html(d: dict) -> str:
    first = escape(_first(d["nombre"]))
    rows = (
        _row("Nombre", d["nombre"])
        + _row("Cédula", d["cedula"])
        + _row("Teléfono", d["telefono"])
        + _row("Condición", d["institucion"])
    )
    return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <title>{EVENT}</title>
</head>
<body style="margin:0;padding:0;background-color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#edf2f7;margin:0;padding:0">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:640px;background-color:#ffffff;margin:0 auto">
          
          <!-- Banner Superior Anti-Dark Mode -->
          <tr>
            <td style="background-color:#1c2a39;padding:32px 24px;border-bottom:4px solid #0082c8">
              <div style="font-size:11px;font-weight:700;color:#68829b;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">
                UNIVERSIDAD DE CARABOBO &bull; FACULTAD DE ODONTOLOGÍA
              </div>
              <div style="font-size:12px;font-weight:700;color:#0082c8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px">
                III JORNADA
              </div>
              <h1 style="color:#ffffff !important;font-size:20px;font-weight:800;margin:0 0 8px;line-height:1.25">
                ACTUALIZACIÓN EN IMPLANTOLOGÍA BUCAL
              </h1>
            </td>
          </tr>

          <!-- Contenido Principal -->
          <tr>
            <td style="padding:28px 20px;background-color:#ffffff">
              <h2 style="font-size:19px;font-weight:700;color:#1c2a39;margin:0 0 8px">
                &iexcl;Hola, {first}!
              </h2>
              <p style="color:#5b738a;font-size:14px;line-height:1.55;margin:0 0 24px">
                Hemos recibido tu solicitud de registro. Tu comprobante de pago está en proceso de verificación por parte del equipo organizador.
              </p>

              <!-- Tabla de Resumen -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e2e8f0">
                {rows}
              </table>

              <!-- Footer -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #e2e8f0;padding-top:20px">
                <tr>
                  <td align="center">
                    <p style="margin:0;font-size:11px;color:#94a3b8">
                      Desarrollado por <a href="{IG_URL}" style="color:#0082c8;font-weight:700;text-decoration:none">Synco</a>
                    </p>
                  </td>
                </tr>
              </table>

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
        api_key = os.environ.get("RESEND_API_KEY")
        if not api_key:
            log.warning("RESEND_API_KEY no encontrada en las variables de entorno.")
            return

        resend.api_key = api_key
        first = _first(d["nombre"])

        text = (
            "Hola " + first + ", tu inscripción a la " + EVENT
            + " quedó agendada para el 21 de noviembre de 2026.\n"
            + "Hemos recibido tu comprobante. Verificaremos los datos y te confirmaremos en breve.\n\n"
            + "Este reporte fue hecho por Synco (" + IG_URL + ")"
        )

        params = {
            "from": f"{EVENT} <contacto@synco-agency.com>",
            "to": [d["correo"]],
            "subject": f"Confirmación de inscripción · {EVENT}",
            "text": text,
            "html": _html(d),
        }

        resend.Emails.send(params)
        log.info("Correo enviado exitosamente vía Resend API a %s", d.get("correo"))

    except Exception:
        log.exception("No se pudo enviar el correo a %s", d.get("correo"))