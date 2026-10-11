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
        + _row("Institución", d["institucion"])
    )
    return f"""\
<!DOCTYPE html>
<html lang="es" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <title>{EVENT}</title>
  <style>
    :root {{ color-scheme: light; supported-color-schemes: light; }}
    body {{ margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #edf2f7 !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table {{ border-collapse: collapse !important; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ border: 0; line-height: 100%; outline: none; text-decoration: none; }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#edf2f7;margin:0;padding:0">
    <tr>
      <td align="center" style="padding:0">
        
        <!-- Main Wrapper Container: Full Width Fit -->
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:640px;background-color:#ffffff;margin:0 auto">
          
          <!-- Banner Superior / Header (Paleta Muted Slate & Cyan UC) -->
          <tr>
            <td style="background-color:#1c2a39;padding:32px 24px;border-bottom:4px solid #0082c8">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="font-size:11px;font-weight:700;color:#68829b;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">
                      UNIVERSIDAD DE CARABOBO &bull; FACULTAD DE ODONTOLOGÍA
                    </div>
                    <div style="font-size:12px;font-weight:700;color:#0082c8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px">
                      III JORNADA
                    </div>
                    <h1 style="color:#ffffff !important;font-size:20px;font-weight:800;margin:0 0 8px;line-height:1.25;letter-spacing:-0.01em;text-transform:uppercase">
                      ACTUALIZACIÓN EN IMPLANTOLOGÍA BUCAL
                    </h1>
                    <div style="font-size:12px;color:#c2d1df;line-height:1.4">
                      Del programa de Especialización en Implantología Bucal
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Contenido Principal -->
          <tr>
            <td style="padding:28px 20px;background-color:#ffffff">
              
              <!-- Saludo -->
              <h2 style="font-size:19px;font-weight:700;color:#1c2a39;margin:0 0 8px;letter-spacing:-0.01em">
                &iexcl;Hola, {first}!
              </h2>
              <p style="color:#5b738a;font-size:14px;line-height:1.55;margin:0 0 24px">
                Hemos recibido tu solicitud de registro. Tu comprobante de pago est&aacute; en proceso de verificaci&oacute;n.
              </p>

              <!-- Box Fecha y Lugar (Coincide con el estilo del afiche) -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f4f7fa;border-left:4px solid #0082c8;margin-bottom:24px">
                <tr>
                  <td style="padding:16px 18px">
                    <div style="font-size:11px;font-weight:800;color:#0082c8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">
                      FECHA &amp; LUGAR DEL EVENTO
                    </div>
                    <div style="font-size:15px;font-weight:800;color:#1c2a39;margin-bottom:2px">
                      21 DE NOVIEMBRE 2026
                    </div>
                    <div style="font-size:13px;font-weight:600;color:#5b738a">
                      INSTITUTO DOCENTE DE UROLOG&Iacute;A
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Tabla con Resumen de Datos -->
              <div style="font-size:12px;font-weight:700;color:#1c2a39;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px">
                Resumen de Inscripci&oacute;n
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e2e8f0;background-color:#ffffff">
                {rows}
              </table>

              <!-- Estado de Confirmación -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#edf2f7;border:1px solid #cbd5e1;margin-bottom:24px">
                <tr>
                  <td style="padding:14px 16px">
                    <p style="margin:0;font-size:13px;color:#23384b;line-height:1.5">
                      <strong>Estatus actual:</strong> Comprobante recibido. Te confirmaremos tu cupo definitivo por este mismo medio una vez validada la transferencia.
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Footer -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #e2e8f0;padding-top:20px;margin-top:12px">
                <tr>
                  <td align="center">
                    <p style="margin:0 0 6px;font-size:12px;color:#68829b">
                      III Jornada de Actualizaci&oacute;n en Implantolog&iacute;a Bucal &bull; UC
                    </p>
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